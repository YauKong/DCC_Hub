"""Smooth Normals tool plugin."""
import math

from hub.core.logging import get_logger
from hub.core.plugins import BaseToolPlugin
from hub.core.qt_import import import_qt

QtWidgets = import_qt()
logger = get_logger(__name__)


class SmoothNormalsTool(BaseToolPlugin):
    """Tool for smoothing normals on selected geometry."""
    
    def __init__(self, context):
        """Initialize plugin with default angle from settings.
        
        Args:
            context: ToolContext instance
        """
        super().__init__(context)
        # Default angle will be determined in create_ui() with priority:
        # 1. state (session memory)
        # 2. settings (persistent)
        # 3. hardcoded default (60.0)
    
    def create_ui(self, parent=None):
        """Create UI widget with angle input and execute button.
        
        Args:
            parent: Parent widget
            
        Returns:
            QWidget containing the plugin UI
        """
        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Get initial angle value with priority: state > settings > default
        state_angle = self.ctx.state.get("poly.smooth_normals.last_angle")
        settings_angle = self.ctx.settings.get("poly.smooth_normals.angle", 60.0)
        
        if state_angle is not None:
            initial_angle = state_angle
            logger.debug(f"Using state angle: {initial_angle}")
        else:
            initial_angle = settings_angle
            logger.debug(f"Using settings/default angle: {initial_angle}")
        
        # Angle input
        angle_label = QtWidgets.QLabel("Angle:")
        self.angle_spinbox = QtWidgets.QDoubleSpinBox()
        self.angle_spinbox.setRange(0.0, 180.0)
        self.angle_spinbox.setValue(initial_angle)
        self.angle_spinbox.setSuffix("°")
        
        angle_layout = QtWidgets.QHBoxLayout()
        angle_layout.addWidget(angle_label)
        angle_layout.addWidget(self.angle_spinbox)
        angle_layout.addStretch()
        
        # Execute button - save reference to prevent garbage collection
        self.execute_button = QtWidgets.QPushButton("Smooth Normals")
        # Connect clicked signal - use lambda to ensure proper binding
        self.execute_button.clicked.connect(lambda checked=False: self._on_execute())
        logger.debug("Button created and connected")
        
        layout.addLayout(angle_layout)
        layout.addWidget(self.execute_button)
        layout.addStretch()
        
        return widget
    
    def _on_execute(self):
        """Handle execute button click - dispatch through CommandBus."""
        angle = self.angle_spinbox.value()
        logger.info(f"Button clicked, dispatching command with angle={angle}")
        
        # Get plugin key (stored by ToolRegistry during instantiation)
        plugin_key = getattr(self, '_plugin_key', None)
        if not plugin_key:
            logger.warning("_plugin_key not found, falling back to direct execute")
            self.execute(angle=angle)
            return
        
        # Dispatch command through CommandBus
        try:
            self.ctx.cmd_bus.dispatch("tool.execute", key=plugin_key, angle=angle)
        except Exception as e:
            logger.error(f"Error dispatching command: {e}", exc_info=True)
    
    def execute(self, **kwargs):
        """Execute smooth normals operation.
        
        Args:
            **kwargs: Plugin parameters (angle, keep_hard)
        """
        angle = kwargs.get('angle', 60.0)
        keep_hard = kwargs.get('keep_hard', False)
        
        try:
            import maya.cmds as cmds
            
            logger.debug("Getting selection...")
            # Get selected objects - refresh selection to get current state
            selection = cmds.ls(sl=True, l=True) or []
            logger.debug(f"Selection: {selection}")
            
            if not selection:
                logger.warning("No selection, showing warning")
                self.ctx.dcc.show_message("No objects selected", level="warning")
                # Still save angle to state even if no selection (user might want to reuse it)
                self.ctx.state["poly.smooth_normals.last_angle"] = angle
                logger.debug(f"Saved angle to state (no selection): {angle}")
                return
            
            # Filter to only polygon meshes
            meshes = []
            for obj in selection:
                # Check if it's a mesh or transform of a mesh
                shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
                for shape in shapes:
                    if cmds.objectType(shape, isType="mesh"):
                        meshes.append(shape)
                        break
                # If no shapes found, check if the object itself is a mesh
                if cmds.objectType(obj, isType="mesh"):
                    meshes.append(obj)
            
            logger.debug(f"Found meshes: {meshes}")
            
            if not meshes:
                logger.warning("No meshes, showing warning")
                self.ctx.dcc.show_message("No polygon meshes selected", level="warning")
                # Still save angle to state even if no meshes (user might want to reuse it)
                self.ctx.state["poly.smooth_normals.last_angle"] = angle
                logger.debug(f"Saved angle to state (no meshes): {angle}")
                return
            
            # Use undo chunk for undo support
            logger.debug("Starting undo chunk...")
            with self.ctx.dcc.undo_chunk("SmoothNormals"):
                # Convert angle from degrees to radians for Maya
                angle_rad = math.radians(angle)
                logger.debug(f"Angle in radians: {angle_rad}")
                
                # Apply polySoftEdge to each mesh
                for mesh in meshes:
                    logger.debug(f"Processing mesh: {mesh}")
                    # Select the mesh first
                    cmds.select(mesh, r=True)
                    # Convert to edges
                    edges = cmds.polyListComponentConversion(mesh, te=True)
                    if edges:
                        cmds.select(edges, r=True)
                        # Apply polySoftEdge to selected edges
                        result = cmds.polySoftEdge(
                            angle=angle_rad,
                            constructionHistory=True
                        )
                        logger.debug(f"polySoftEdge result: {result}")
            
            logger.info(f"Completed smoothing normals on {len(meshes)} mesh(es)")
            self.ctx.dcc.show_message(f"Smoothed normals on {len(meshes)} mesh(es)", level="info")
            
            # Save angle to state for session memory
            self.ctx.state["poly.smooth_normals.last_angle"] = angle
            logger.debug(f"Saved angle to state: {angle}")
        except ImportError:
            # Not in Maya environment
            selection = self.ctx.dcc.get_selection()
            logger.debug(f"execute(angle={angle}, keep_hard={keep_hard})")
            logger.debug(f"  Selection: {selection}")
            # Save angle to state even in non-Maya environment
            self.ctx.state["poly.smooth_normals.last_angle"] = angle
        except Exception as e:
            self.ctx.dcc.show_message(f"Error: {str(e)}", level="error")
            logger.error(f"Error executing smooth normals: {e}", exc_info=True)
            # Still save angle to state even on error (user might want to reuse it)
            self.ctx.state["poly.smooth_normals.last_angle"] = angle
            logger.debug(f"Saved angle to state (error): {angle}")


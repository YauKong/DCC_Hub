"""Smooth Normals tool plugin."""
import math

from hub.core.plugins import BaseToolPlugin
from hub.core.qt_import import import_qt

QtWidgets = import_qt()


class SmoothNormalsTool(BaseToolPlugin):
    """Tool for smoothing normals on selected geometry."""
    
    def create_ui(self, parent=None):
        """Create UI widget with angle input and execute button.
        
        Args:
            parent: Parent widget
            
        Returns:
            QWidget containing the plugin UI
        """
        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QVBoxLayout(widget)
        
        # Angle input
        angle_label = QtWidgets.QLabel("Angle:")
        self.angle_spinbox = QtWidgets.QDoubleSpinBox()
        self.angle_spinbox.setRange(0.0, 180.0)
        self.angle_spinbox.setValue(60.0)
        self.angle_spinbox.setSuffix("°")
        
        angle_layout = QtWidgets.QHBoxLayout()
        angle_layout.addWidget(angle_label)
        angle_layout.addWidget(self.angle_spinbox)
        angle_layout.addStretch()
        
        # Execute button - save reference to prevent garbage collection
        self.execute_button = QtWidgets.QPushButton("Smooth Normals")
        # Connect clicked signal - use lambda to ensure proper binding
        self.execute_button.clicked.connect(lambda checked=False: self._on_execute())
        print("[SmoothNormalsTool] Button created and connected")
        
        layout.addLayout(angle_layout)
        layout.addWidget(self.execute_button)
        layout.addStretch()
        
        return widget
    
    def _on_execute(self):
        """Handle execute button click - dispatch through CommandBus."""
        print("[SmoothNormalsTool] Button clicked")
        angle = self.angle_spinbox.value()
        print(f"[SmoothNormalsTool] Dispatching command with angle={angle}")
        
        # Get plugin key (stored by ToolRegistry during instantiation)
        plugin_key = getattr(self, '_plugin_key', None)
        if not plugin_key:
            print("[SmoothNormalsTool] Warning: _plugin_key not found, falling back to direct execute")
            self.execute(angle=angle)
            return
        
        # Dispatch command through CommandBus
        try:
            self.ctx.cmd_bus.dispatch("tool.execute", key=plugin_key, angle=angle)
        except Exception as e:
            print(f"[SmoothNormalsTool] Error dispatching command: {e}")
            import traceback
            traceback.print_exc()
    
    def execute(self, **kwargs):
        """Execute smooth normals operation.
        
        Args:
            **kwargs: Plugin parameters (angle, keep_hard)
        """
        angle = kwargs.get('angle', 60.0)
        keep_hard = kwargs.get('keep_hard', False)
        
        try:
            import maya.cmds as cmds
            
            print("[SmoothNormalsTool] Getting selection...")
            # Get selected objects - refresh selection to get current state
            selection = cmds.ls(sl=True, l=True) or []
            print(f"[SmoothNormalsTool] Selection: {selection}")
            
            if not selection:
                print("[SmoothNormalsTool] No selection, showing warning")
                self.ctx.dcc.show_message("No objects selected", level="warning")
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
            
            print(f"[SmoothNormalsTool] Found meshes: {meshes}")
            
            if not meshes:
                print("[SmoothNormalsTool] No meshes, showing warning")
                self.ctx.dcc.show_message("No polygon meshes selected", level="warning")
                return
            
            # Use undo chunk for undo support
            print("[SmoothNormalsTool] Starting undo chunk...")
            with self.ctx.dcc.undo_chunk("SmoothNormals"):
                # Convert angle from degrees to radians for Maya
                angle_rad = math.radians(angle)
                print(f"[SmoothNormalsTool] Angle in radians: {angle_rad}")
                
                # Apply polySoftEdge to each mesh
                for mesh in meshes:
                    print(f"[SmoothNormalsTool] Processing mesh: {mesh}")
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
                        print(f"[SmoothNormalsTool] polySoftEdge result: {result}")
            
            print(f"[SmoothNormalsTool] Completed, showing success message")
            self.ctx.dcc.show_message(f"Smoothed normals on {len(meshes)} mesh(es)", level="info")
        except ImportError:
            # Not in Maya environment
            selection = self.ctx.dcc.get_selection()
            print(f"SmoothNormalsTool.execute(angle={angle}, keep_hard={keep_hard})")
            print(f"  Selection: {selection}")
        except Exception as e:
            self.ctx.dcc.show_message(f"Error: {str(e)}", level="error")
            print(f"[SmoothNormalsTool] Error: {e}")
            import traceback
            traceback.print_exc()


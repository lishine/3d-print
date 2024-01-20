# %%

from build123d import *
from ocp_vscode import *


# %%

reset_show()
set_defaults(
    reset_camera=Camera.KEEP,
    default_opacity=0.7,
    transparent=False,
)

with BuildPart() as p:
    Box(100, 10, 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    Box(80, 10, 1.6, mode=Mode.SUBTRACT, align=(Align.CENTER, Align.CENTER, Align.MIN))


show(p)
p.part.export_stl("bridge.stl")

# %%
from math import pi
from build123d import *
from ocp_vscode import *
import numpy as np

# %%
reset_show()


def pseudo_fillet(v: Vertex, radius: float, dir_x=-1, dir_y=-1):
    vec = Vector(v.X, v.Y)

    with BuildSketch() as sk:
        with BuildLine():
            arc = RadiusArc(
                vec + (radius * dir_x, 0), vec + (0, radius * dir_y), radius=radius
            )
            Polyline(arc @ 0, vec, arc @ 1)
            show_object(arc)
        make_face()
    return sk


with BuildSketch() as sk:
    Rectangle(10, 10)
    v = sk.vertices().group_by(Axis.X)[-1].sort_by(Axis.Y)[-1]
    add(sk.faces()[0].fillet_2d(vertices=[v], radius=1))
    # add(pseudo_fillet(v, 10, -1, -1), mode=Mode.SUBTRACT)
show_object(sk)

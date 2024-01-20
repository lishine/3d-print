# %%
from math import pi
from build123d import *
from ocp_vscode import *
import numpy as np
from enum import Enum


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
# %%
reset_show()

with BuildPart() as bp:
    with BuildSketch() as bs:
        with BuildLine() as bl:
            p1 = (0, 5)
            p2 = (20, 10)
            middle = ((p2[0] + p1[0]) / 2, (p2[1] + p1[1]) / 2)
            l3 = Spline(p1, middle, p2, tangents=((1, 0), (2, 6), (1, 0)))
            show_object(l3, "l3")
            mirror(about=Plane.XZ)
        make_face()
    extrude(amount=3)
# show_object(bp)
# %%

reset_show()
set_defaults(
    reset_camera=Camera.KEEP,
    default_opacity=0.7,
    transparent=False,
)


with BuildPart() as p:
    # DISC

    class disc:
        w = 100
        t = 2

    Cylinder(radius=disc.w / 2, height=disc.t)
    topf = p.faces().sort_by(Axis.Z)[-1]

    # SLOTS

    class slots:
        w = 2
        margin = 5
        min_in_margin = 4
        min_out_margin = 5
        arc_angle_size = 45
        min_angle_size = 10
        arc_gap = 5

    slot_delta = slots.margin + slots.w
    n = ((disc.w / 2 - slots.min_in_margin - slots.min_out_margin) / slot_delta) // 1
    disc_calc_margin = (
        disc.w / 2 - slots.min_in_margin - slots.min_out_margin - n * slot_delta
    ) / 2

    def arc_angle_gap(r: int):
        return 360 * slots.arc_gap / (2 * pi * r)

    with BuildSketch(topf) as part_sk_slots:
        for rotation in range(0, 360, slots.arc_angle_size):
            for r in np.arange(
                slots.min_in_margin + disc_calc_margin,
                disc.w / 2 - disc_calc_margin - slots.min_out_margin + 0.1,
                slot_delta,
            ):
                skip = False
                if r > disc.w / 4:
                    arc_angle_actual_size = slots.arc_angle_size - arc_angle_gap(r)
                else:
                    arc_angle_actual_size = slots.arc_angle_size * 2 - arc_angle_gap(r)
                    skip = rotation % (2 * slots.arc_angle_size) > 0
                if not skip:
                    with BuildLine(mode=Mode.PRIVATE) as part_ln:
                        CenterArc(
                            center=(0, 0),
                            radius=r,
                            start_angle=rotation,
                            arc_size=arc_angle_actual_size,
                        )
                    SlotArc(arc=part_ln.edges()[0], height=slots.w)
    extrude(amount=-disc.t, mode=Mode.SUBTRACT)

    ## DISC FRAME

    class frame:
        w = 2
        t = 2

    with BuildSketch(topf) as part_sk_disc_frame:
        Circle(disc.w / 2)
        Circle((disc.w / 2) - frame.w, mode=Mode.SUBTRACT)
    extrude(amount=frame.t)

    # BOTTOM PART

    class insert:
        down_D = 50.5
        up_D = 46
        h = 13 + frame.t
        top_H = 2.5
        t = 1.5
        cut_slot_w = 10

    ## Loft Cylinder

    with BuildSketch(topf) as s:
        Circle(radius=insert.down_D / 2)
    with BuildSketch(topf.offset(insert.h)) as s2:
        Circle(radius=insert.up_D / 2)
    loft()

    with BuildSketch(topf) as s:
        Circle(radius=insert.down_D / 2 - insert.t)
    with BuildSketch(topf.offset(insert.h)) as s2:
        Circle(radius=insert.up_D / 2 - insert.t)
    loft(mode=Mode.SUBTRACT)

    ## Base

    h_extra = 0.5
    r_extra = insert.t * 1.5
    with BuildSketch(topf.offset(h_extra)) as s:
        Circle(radius=r_extra + insert.down_D / 2)
        Circle(radius=insert.down_D / 2 - insert.t - r_extra, mode=Mode.SUBTRACT)
    extrude(amount=-disc.t - h_extra)
    selected = [p.edges().group_by(Axis.Z)[4][i] for i in [2, 3]]
    fillet(selected, radius=1.5 * (r_extra / 2))

    ## Cut Slots

    cutDia = insert.down_D * 1.1
    for rotation in range(0, 136, 45):
        with BuildSketch(topf) as s1:
            Rectangle(insert.cut_slot_w, cutDia, rotation=rotation)
        with BuildSketch(topf.offset(insert.h - insert.top_H)) as s2:
            Rectangle(insert.cut_slot_w / 2, cutDia, rotation=rotation)
        loft(mode=Mode.SUBTRACT)
    selected = p.part.edges().group_by(Axis.Z)[-3].filter_by(GeomType.LINE)
    fillet(selected, radius=3)

    selected = p.edges().group_by(Axis.Z)[0].sort_by(Axis.X)[0]
    chamfer(selected, length=disc.t * 1.5)

p.part.export_stl("drain.stl")
show_object(p)

# %%

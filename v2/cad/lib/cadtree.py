"""A small part tree for Dimer models, and a STEP writer that keeps names, colours and face colours.

Node(name, children, loc)        a folder: an assembly in the STEP file, with its own placement
Leaf(name, shape, rgb, faces)    one solid; `faces` is an optional list of rgb, one per face in shape.Faces() order
                                 (KiCad parts come as one solid with coloured faces: pins gold, body black)

write_step(node, path) writes it with XCAF so CAD programs see the tree, the names and the colours.
flatten(node) gives (path, shape in world position, rgb, faces) for clash checks and meshes.
"""
import cadquery as cq
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.TDataStd import TDataStd_Name
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.Interface import Interface_Static
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopLoc import TopLoc_Location


class Leaf:
    def __init__(self, name, shape, rgb, faces=None):
        if isinstance(shape, cq.Workplane):
            shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
        self.name, self.shape, self.rgb, self.faces = name, shape, tuple(rgb), faces


class Node:
    def __init__(self, name, children=None, loc=None):
        self.name, self.children, self.loc = name, list(children or []), loc or cq.Location()

    def add(self, child, loc=None):
        if loc is not None:
            child.loc = loc * child.loc if isinstance(child, Node) else loc
            if isinstance(child, Leaf):     # a placed leaf becomes a one-leaf folder so it keeps its own frame
                child = Node(child.name, [Leaf(child.name, child.shape, child.rgb, child.faces)], loc)
        self.children.append(child)
        return child


def flatten(node, loc=None, path=""):
    loc = (loc or cq.Location()) * node.loc if isinstance(node, Node) else (loc or cq.Location())
    if isinstance(node, Leaf):
        yield path + node.name, node.shape.moved(loc), node.rgb, node.faces
        return
    for ch in node.children:
        yield from flatten(ch, loc, path + node.name + "/")


def _col(rgb):
    return Quantity_Color(float(rgb[0]), float(rgb[1]), float(rgb[2]), Quantity_TOC_RGB)


def write_step(root, path, pcurves=False):
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    st.SetAutoNaming_s(False)
    surf = XCAFDoc_ColorType.XCAFDoc_ColorSurf

    def build(node):
        if isinstance(node, Leaf):
            lab = st.AddShape(node.shape.wrapped, False)
            TDataStd_Name.Set_s(lab, TCollection_ExtendedString(node.name))
            ct.SetColor(lab, _col(node.rgb), surf)
            if node.faces:
                for f, c in zip(node.shape.Faces(), node.faces):
                    if tuple(c) != tuple(node.rgb):
                        sub = st.AddSubShape(lab, f.wrapped)
                        if not sub.IsNull():
                            ct.SetColor(sub, _col(c), surf)
            return lab
        lab = st.NewShape()
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(node.name))
        for ch in node.children:
            cl = build(ch)
            loc = ch.loc.wrapped if isinstance(ch, Node) else TopLoc_Location()
            comp = st.AddComponent(lab, cl, loc)
            TDataStd_Name.Set_s(comp, TCollection_ExtendedString(ch.name))
        return lab

    build(root)
    st.UpdateAssemblies()
    Interface_Static.SetIVal_s("write.surfacecurve.mode", 1 if pcurves else 0)
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPCAFControl_Writer()
    w.SetColorMode(True); w.SetNameMode(True)
    w.Transfer(doc, STEPControl_AsIs)
    if w.Write(path) != IFSelect_RetDone:
        raise IOError("could not write " + path)


def mesh(node, tol=0.05, ang=0.3, round_to=3):
    """Triangles grouped by part folder (first level under root) and colour, for the web viewer."""
    out = {}
    for p, shape, rgb, faces in flatten(node):
        key = p.split("/")[1] if p.count("/") > 1 else p
        for i, f in enumerate(shape.Faces()):
            c = tuple(round(x, 3) for x in (faces[i] if faces else rgb))
            try:
                v, t = f.tessellate(tol, ang)
            except Exception:
                continue
            if not t:
                continue
            g = out.setdefault(key, {}).setdefault(c, ([], []))
            base = len(g[0]) // 3
            g[0].extend(round(x, 2) for vv in v for x in vv.toTuple())
            g[1].extend(base + i_ for tri in t for i_ in tri)
    return out

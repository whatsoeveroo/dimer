"""Read a STEP file with its colours and names, flattened to (name, solid, rgb, face_rgbs) leaves in world position.
rgb is the colour covering most of the solid; face_rgbs has one colour per face in solid.Faces() order.

CadQuery's Assembly.importStep refuses files where two parts share a name (KiCad exports do that),
so this walks the XCAF document directly.
"""
import cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType, XCAFDoc_ColorTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.Quantity import Quantity_Color
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.IFSelect import IFSelect_RetDone


def _name(label):
    attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), attr):
        return attr.Get().ToExtString()
    return ""


def load(path, default=(0.6, 0.6, 0.6)):
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True)
    if r.ReadFile(path) != IFSelect_RetDone:
        raise IOError("cannot read " + path)
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    out = []

    def colour_of(label, shape, inherited):
        c = Quantity_Color()
        for typ in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
            if XCAFDoc_ColorTool.GetColor_s(label, typ, c) or ct.GetColor(shape, typ, c):
                return (c.Red(), c.Green(), c.Blue())
        return inherited

    def walk(label, loc, inherited, name):
        if st.IsAssembly_s(label):
            comps = TDF_LabelSequence(); st.GetComponents_s(label, comps)
            for i in range(1, comps.Length() + 1):
                cl = comps.Value(i); ref = TDF_Label(); st.GetReferredShape_s(cl, ref)
                l2 = loc * st.GetLocation_s(cl)
                col = colour_of(cl, st.GetShape_s(cl), inherited)
                nm = _name(ref) if not _name(ref).startswith("=>") else (_name(cl) or name)
                walk(ref, l2, colour_of(ref, st.GetShape_s(ref), col), nm or name)
            return
        shape = st.GetShape_s(label)
        col = colour_of(label, shape, inherited)
        subs = TDF_LabelSequence(); st.GetSubShapes_s(label, subs)
        fcol = {}                      # face hash -> colour, from coloured sub-shapes (faces or whole solids)
        for i in range(1, subs.Length() + 1):
            sl = subs.Value(i); ss = st.GetShape_s(sl)
            c = colour_of(sl, ss, None)
            if c is None:
                continue
            for f in cq.Shape.cast(ss).Faces():
                fcol[hash(f)] = c
        base = cq.Shape.cast(shape)
        solids = base.Solids() or [base]
        for so in solids:              # one leaf per solid, coloured by the colour covering most of its area
            area = {}
            for f in so.Faces():
                c = fcol.get(hash(f), col or default)
                area[c] = area.get(c, 0) + f.Area()
            c = max(area, key=area.get) if area else (col or default)
            faces = [fcol.get(hash(f), col or default) for f in so.Faces()]
            out.append((name or _name(label), cq.Shape.cast(so.wrapped.Moved(loc)), c, faces))

    roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1):
        lb = roots.Value(i)
        walk(lb, TopLoc_Location(), colour_of(lb, st.GetShape_s(lb), None), _name(lb))
    return out

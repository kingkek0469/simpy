""" Output configuration files, current support data, geo, xyz.
11-10-2012: add head in geo output
01-04-2013: debug toPdb
@todo: finish to Top
"""
import numpy as np
from cons import ELEMENT2MASS, ELEMENT2ATN
from utilities import lattice2v

def toReaxLammps(system, outfile="lammps.data"):
    """ output to lammps data file
    """

    o = open(outfile, 'w')
    o.write("# \n")
    o.write("\n")
    o.write("%d atoms\n\n"%len(system.atoms))
    o.write("%d atom types\n\n"%len(system.map))
    pbc = system.pbc
    if len(pbc) >= 6:
        if pbc[3] == 90.0 and pbc[4] == 90 and pbc[5] == 90:
            o.write(" 0.0 %9.4f xlo xhi\n"%pbc[0])
            o.write(" 0.0 %9.4f ylo yhi\n"%pbc[1])
            o.write(" 0.0 %9.4f zlo zhi\n"%pbc[2])
        else:
            xx, xy, xz, yy, yz, zz = lattice2v(pbc)
            o.write(" 0.0 %9.4f xlo xhi\n"%xx)
            o.write(" 0.0 %9.4f ylo yhi\n"%yy)
            o.write(" 0.0 %9.4f zlo zhi\n"%zz)
            o.write("%9.4f%9.4f%9.4f xy xz yz\n\n"%(xy, xz, yz))        
    else:
        print "Warning: No box found. Using a default box 5.0 * 5.0 * 5.0"
        o.write(" %9.4f %9.4f xlo xhi\n"%(-25.0, 25.0))
        o.write(" %9.4f %9.4f ylo yhi\n"%(-25.0, 25.0))
        o.write(" %9.4f %9.4f zlo zhi\n"%(-25.0, 25.0))
    o.write("Masses\n\n")
    for i in system.map:
        # atom name 
        atn = ''
        for j in i[1]:
            if j.isdigit():
                break
            atn += j
        o.write("%d %s # %s\n"%(i[0], ELEMENT2MASS[atn], atn))
    o.write("\n")
    o.write("Atoms\n")
    o.write("\n")

    counter = 1
    for i in system.atoms:
        line = ''
        line += "%-6d"%counter
        line += "%3d"%i.type1
        line += "%10.6f"%i.charge
        line += "%12.6f"%i.x[0]
        line += "%12.6f"%i.x[1]
        line += "%12.6f"%i.x[2]
        line += "\n"
        o.write(line)
        counter += 1

    o.close()
    
def toGeo(system, outfile="test.geo"):
    """ output to geo file format
    """
    o = open(outfile, 'w')
    if system.pbc:
        o.write("%s\n"%"XTLGRF 200")
    else:
        o.write("%s\n"%system.geotag)
    o.write("DESCRP %s\n"%system.name)
    o.write("REMARK generated by simulation python\n")
    if len(system.redundant) > 0:
        for i in system.redundant:
            if i[0] == "B":
                a1 = int(i[1])
                a2 = int(i[2])
                bond = float(i[3])
                line = "BOND RESTRAINT    %d   %d  %.4f 7500.00  1.0000  0.0000000       0       0\n"%(a1, a2, bond)
                o.write(line)
            elif i[0] == "D":
                a1 = int(i[1])
                a2 = int(i[2])
                a3 = int(i[3])
                a4 = int(i[4])
                angle = float(i[5])
                line = "TORSION RESTRAINT    %d   %d   %d   %d  %.4f  500.00  5.0000  0.0000000\n"%(a1, a2, a3, a4, angle)
                o.write(line)
    #o.write("FORMAT ATOM   (a6,1x,i5,1x,a5,1x,a3,1x,a1,1x,a5,3f10.5,1x,a5,i3,i2,1x,f8.5)\n")
    if system.pbc:
        o.write("CRYSTX %s\n"%(''.join(["%11.5f"%i for i in system.pbc])))
    counter = 1
    for i in system.atoms:
        line = ''
        line += "%6s"%"HETATM"
        line += " "
        line += "%5d"%counter
        line += " "
        line += "%-5s"%i.name
        line += "%12s"%""
        line += "%10.5f"%i.x[0]
        line += "%10.5f"%i.x[1]
        line += "%10.5f"%i.x[2]
        line += "%4s"%" "
        line += "%-2s"%i.element
        line += "%3d"%0
        line += "%2d"%0
        line += "%9.5f"%0
        line += "\n"
        o.write(line)
        counter += 1
    o.write("END\n")
    o.write("\n")
    o.close()

def toXyz(system, outfile="test.xyz"):
    """ output to xyz file format
    """
    o = open(outfile, 'w')
    o.write("%d\n"%len(system.atoms))
    o.write("%s\n"%system.name)
    for i in system.atoms:
        line = ''
        line += "%-6s"%i.name
        line += "%10.4f"%i.x[0]
        line += "%10.4f"%i.x[1]
        line += "%10.4f"%i.x[2]
        line += "\n"
        o.write(line)
    o.close()

def toPdb(system, outfile="test.pdb", element=0):
    """ output to pdb file format
    """
    o = open(outfile, 'w')
    #o.write("TITLE %s\n"%system.name)
    o.write("REMARK Generated by simpy\n")
    #print system.pbc
    if system.pbc:
        o.write("CRYST1")
        o.write("".join(["%9.3f"%i for i in system.pbc[:3]]))
        o.write("".join(["%7.2f"%i for i in system.pbc[3:]]))
        o.write(" P 1           1\n")
    o.write("MODEL        1\n")
    counter = 1
    for i in system.atoms:
        o.write("HETATM")
        o.write("%5d"%counter)
        if len(i.name) > 4:
            i.name = i.name[:4]
        if element:
            i.name = i.element
        o.write("%4s"%i.name)
        o.write("%5s"%"LIG")
        o.write("%6d"%counter)
        o.write("%12.3f"%i.x[0])
        o.write("%8.3f"%i.x[1])
        o.write("%8.3f"%i.x[2])
        o.write("%6.2f"%1.0)
        o.write("%6.2f"%0.0)
        o.write("%12s"%i.name)
        o.write("\n")
        counter += 1
    o.write("TER\n")
    o.write("ENDMDL\n")
    o.close()

def toGjf(system, outfile="g03out.gjf"):
    """output the gjf file
    """
    o = open(outfile, "w")
    if len(system.options) > 0:
        for i in system.options:
            o.write(i.strip() + '\n')
    if len(system.methods) > 0:
        for i in system.methods:
            o.write("# " + i.strip() + '\n')
    o.write('\n')
    o.write(system.name + "\n")
    o.write('\n')
    o.write('%d %d\n'%(system.charge, system.spin))
    if len(system.atoms) > 0:
        for i in system.atoms:
            o.write("%-5s"%i.name)
            o.write("%10.5f"%i.x[0])
            o.write("%10.5f"%i.x[1])
            o.write("%10.5f"%i.x[2])
            o.write("\n")
    o.write('\n')
    if len(system.connect) > 0:
        for i in system.connect:
            o.write(" " + i.strip() + '\n')

    o.write('\n')
    if len(system.redundant) > 0:
        for i in system.redundant:
            o.write(" ".join(i) + '\n')
            
    o.write('\n')
    o.write('\n')
    o.write('\n')
    o.close()

def toTop(system, outfile="topol.top"):
    """output the top file
    """
    o = open(outfile, "w")
    o.write('include "vdw.itp"\n')
    o.write("[ moleculetype ]\n")
    o.write("simpy     3\n")
    o.write("\n")
    o.write("[ atoms ]\n")
    """
         1        o_2w     1         WAT           O     1     -0.8476    15.99940
    [ system ]
    ; Name
    HEP_2

    [ molecules ]
    ;      Compound     #mols
    WAT_1  1024
    HEP_2     1
    """

def toDump(system, outfile="output.dump"):
    """Output the dump file
    """
    o = open(outfile, "w")
    o.write("ITEM: TIMESTEP\n")
    o.write("%d\n"%system.step)
    o.write("ITEM: NUMBER OF ATOMS\n")
    o.write("%d\n"%len(system.atoms))
    # write the pbc
    pbc = system.pbc
    """ITEM: BOX BOUNDS xy xz yz xx yy zz 
       xlo_bound xhi_bound xy
       ylo_bound yhi_bound xz
       zlo_bound zhi_bound yz 
    """
    if len(pbc) >= 6:
        if pbc[3] == 90.0 and pbc[4] == 90 and pbc[5] == 90:
            o.write("ITEM: BOX BOUNDS pp pp pp\n")
            o.write(" 0.0 %9.4f 0.0\n"%pbc[0])
            o.write(" 0.0 %9.4f 0.0\n"%pbc[1])
            o.write(" 0.0 %9.4f 0.0\n"%pbc[2])
        else:
            o.write("ITEM: BOX BOUNDS xy xz yz pp pp pp\n")
            xx, xy, xz, yy, yz, zz = lattice2v(pbc)
            o.write(" %9.4f %9.4f %9.4f\n"%(xz, xx, xy))
            o.write(" 0.0 %9.4f %9.4f\n"%(yy, xz))
            o.write(" 0.0 %9.4f %9.4f\n"%(zz, yz))
    else:
        print "Warning: No box found. Using a default box 5.0 * 5.0 * 5.0"
        o.write(" 0.0 %9.4f xlo xhi\n"%5.0)
        o.write(" 0.0 %9.4f ylo yhi\n"%5.0)
        o.write(" 0.0 %9.4f zlo zhi\n"%5.0)
    o.write("ITEM: ATOMS id type x y z\n")

    for i in system.atoms:
        o.write("%-9d"%i.an)
        o.write("%6d"%i.type1)
        o.write("%14.6f"%i.x[0])
        o.write("%14.6f"%i.x[1])
        o.write("%14.6f"%i.x[2])
        o.write("\n")
    o.close()

def toMsd(system, outfile="dff.msd"):
    """Output the msd file
    """
    o = open(outfile, "w")
    o.write("#Associated PPF =\n") 
    o.write("#DFF:MSD\n")
    o.write("#Model Structure Data File    Energy = 0.0\n")
    pbc = system.pbc
    if len(pbc) >= 6:
        o.write("PBC: ")
        o.write("%9.4f%9.4f%9.4f"%(pbc[0], pbc[1], pbc[2]))
        o.write("%6.2f%6.2f%6.2f\n"%(pbc[3], pbc[4], pbc[5]))

    system.assignEleTypes()
    o.write("%-d\n"%len(system.atoms))
    n = 1
    for i in system.atoms:
        step = n
        atp1 = i.element
        atp2 = i.element
        atp3 = i.element
        an = ELEMENT2ATN[atp1]
        q = 0.0
        o.write("%-8d"%step)
        o.write("%5s"%atp1)
        o.write("%5d"%an)
        o.write("%5s"%atp2)
        o.write("%5s"%atp3)
        o.write("%10.4f"%q)
        o.write("%12.6f"%i.x[0])
        o.write("%12.6f"%i.x[1])
        o.write("%12.6f"%i.x[2])
        o.write(" 1  UNK  0\n")
        n += 1

    o.write("%-d\n"%len(system.connect))
    for i in system.connect:
        o.write("%-6d%-6d%4d\n"%(i[0], i[1], 1))
    o.write("#DFF:END\n")
    o.close()
        
    o.write
    o.close()

def toPoscar(system, outfile="POSCAR"):
    """Output the msd file
    """
    s = system
    o = open(outfile, "w")
    o.write("%s\n"%s.name) 
    o.write("%20.15f\n"%s.scaleFactor)

    xx, xy, xz, yy, yz, zz = lattice2v(s.pbc)
    a = [xx, 0.0, 0.0]
    b = [xy, yy, 0.0]
    c = [xz, yz, zz]

    """
    latvecs = np.array([a, b, c], dtype=float)
    invlatvecs = np.linalg.inv(latvecs)
    [xf, yf, zf] = np.dot(coords[i], invlatvecs)
    """

    for i in a:
        o.write("%20.15f"%i)
    o.write("\n")
    for i in b:
        o.write("%20.15f"%i)
    o.write("\n")
    for i in c:
        o.write("%20.15f"%i)
    o.write("\n")
    for i in s.atomtypes:
        o.write("%6s"%i)
    o.write("\n")
    for i in s.natoms:
        o.write("%6d"%i)
    o.write("\n")
    o.write("Selective dynamics\n")
    o.write("Direct\n")
    coords = []
    coordsXr = []
    natom = 0
    for i in s.atoms:
        coords.append(np.array(i.xFrac))
        coordsXr.append(i.xr)
        natom += 1

    for i in range(natom):
        xf = coords[i][0]
        yf = coords[i][1]
        zf = coords[i][2]
        o.write("%20.15f%20.15f%20.15f"%(xf, yf, zf))
        xr = "T"
        yr = "T"
        zr = "T"
        if coordsXr[i][0] == 1:
            xr = "F"
        if coordsXr[i][1] == 1:
            yr = "F"
        if coordsXr[i][2] == 1:
            zr = "F"
        o.write("%4s%4s%4s\n"%(xr, yr, zr))
    o.write("\n")
    o.close()

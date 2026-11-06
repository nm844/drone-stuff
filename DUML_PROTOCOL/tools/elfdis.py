#!/usr/bin/env python3
"""Helper: dump bytes / disassemble ARM Thumb/ARM functions from an ELF by vaddr, using pyelftools for addr->offset mapping and capstone for disasm."""
import sys
from elftools.elf.elffile import ELFFile

def addr_to_offset(elf, vaddr):
    for seg in elf.iter_segments():
        if seg['p_type'] != 'PT_LOAD':
            continue
        if seg['p_vaddr'] <= vaddr < seg['p_vaddr'] + seg['p_filesz']:
            return seg['p_offset'] + (vaddr - seg['p_vaddr'])
    return None

def read_bytes(path, vaddr, size):
    with open(path, 'rb') as f:
        elf = ELFFile(f)
        off = addr_to_offset(elf, vaddr)
        if off is None:
            raise ValueError(f"vaddr {hex(vaddr)} not mapped")
        f.seek(off)
        return f.read(size)

def disasm(path, vaddr, size, thumb=True):
    import capstone
    data = read_bytes(path, vaddr & ~1, size)
    mode = capstone.CS_MODE_THUMB if thumb else capstone.CS_MODE_ARM
    md = capstone.Cs(capstone.CS_ARCH_ARM, mode)
    md.detail = True
    out = []
    for insn in md.disasm(data, vaddr & ~1):
        out.append(f"0x{insn.address:08x}:\t{insn.mnemonic}\t{insn.op_str}")
    return "\n".join(out)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('vaddr')
    ap.add_argument('size')
    ap.add_argument('--arm', action='store_true')
    ap.add_argument('--bytes', action='store_true')
    args = ap.parse_args()
    vaddr = int(args.vaddr, 0)
    size = int(args.size, 0)
    if args.bytes:
        data = read_bytes(args.path, vaddr & ~1, size)
        print(data.hex())
    else:
        print(disasm(args.path, vaddr, size, thumb=not args.arm))

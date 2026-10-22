#!/usr/bin/env python3
"""
Quick syntax check of Swift files (no type checking) with tree-sitter.
    pip install tree-sitter tree-sitter-swift
    python3 prismgram/check_swift_syntax.py file1.swift file2.swift ...
Used by CI to catch broken patches before the long macOS build.
"""
import sys, tree_sitter_swift as tss, tree_sitter as ts
lang = ts.Language(tss.language()); parser = ts.Parser(lang)
def errors(node, out):
    if node.type == 'ERROR' or node.is_missing:
        out.append(node)
    for c in node.children:
        errors(c, out)
bad = 0
for path in sys.argv[1:]:
    src = open(path, 'rb').read()
    tree = parser.parse(src)
    errs = []; errors(tree.root_node, errs)
    if errs:
        bad += 1
        for e in errs[:5]:
            print(f"{path}:{e.start_point[0]+1}:{e.start_point[1]+1}: {'missing '+e.type if e.is_missing else 'syntax error'}")
    else:
        print(f"ok {path}")
sys.exit(1 if bad else 0)

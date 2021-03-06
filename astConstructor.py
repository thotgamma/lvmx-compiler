import json
import node
import glob as g
import MODEL as m
from pycparser import CParser, c_parser, c_ast, parse_file

def escapeString(string):
    string = string.replace(r'\n', '\n')
    string = string.replace(r'\t', '\n')
    string = string.replace(r'\r', '\n')
    string = string.replace(r'\0', '\0')
    string = string.replace(r'\"', '\"')
    string = string.replace(r'\'', '\'')
    return string


def projectAST(ast, s = 0):

    if (ast is None):
        return None

    elif isinstance(ast, c_ast.ArrayDecl):
        return projectAST(ast.type, s).setLength(projectAST(ast.dim, s)) #MEMO dim_quals unused

    elif isinstance(ast, c_ast.ArrayRef): # [name*, subscript*]
        return node.Indirect(a2t(ast), node.Add(a2t(ast), projectAST(ast.name, s), projectAST(ast.subscript, s)))

    elif isinstance(ast, c_ast.Assignment): # [op, lvalue*, rvalue*]
        if ast.op == '=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s))
        elif ast.op == '+=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Add(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '-=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Sub(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '*=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Mul(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '/=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Div(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '%=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Mod(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '<<=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.LShift(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '>>=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.RShift(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '&=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.And(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '|=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Or(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        elif ast.op == '^=':
            return node.Assign(a2t(ast), projectAST(ast.lvalue, s), node.Xor(a2t(ast), projectAST(ast.lvalue, s), projectAST(ast.rvalue, s)))
        else:
            g.r.addReport(m.Report('fatal', a2t(ast), f"unsupported assignment op '{ast.op}'"))
            return

    elif isinstance(ast, c_ast.BinaryOp): # [op, left* right*]
        if ast.op == '+':
            return node.Add(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '-':
            return node.Sub(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '*':
            return node.Mul(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '/':
            return node.Div(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '%':
            return node.Mod(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '<<':
            return node.LShift(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '>>':
            return node.RShift(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '&':
            return node.And(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '|':
            return node.Or(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '^':
            return node.Xor(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '<':
            return node.Lt(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '<=':
            return node.Lte(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '>':
            return node.Gt(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '>=':
            return node.Gte(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '==':
            return node.Eq(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '!=':
            return node.Neq(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '&&':
            return node.And(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        elif ast.op == '||':
            return node.Or(a2t(ast), projectAST(ast.left, s), projectAST(ast.right, s))
        else:
            g.r.addReport(m.Report('fatal', a2t(ast), f"unsupported binary op '{ast.op}'"))
            return

    elif isinstance(ast, c_ast.Break): # []
        return node.Break(a2t(ast))

    elif isinstance(ast, c_ast.Case): # [expr*, stmts**]
        return [projectAST(ast.expr, s), [projectAST(e, s+1) for e in ast.stmts]]

    elif isinstance(ast, c_ast.Cast): # [to_type*, expr*]
        return node.Cast(a2t(ast), projectAST(ast.to_type, s), projectAST(ast.expr, s))

    elif isinstance(ast, c_ast.Compound): # [block_items**]
        if ast.block_items is None:
            return node.Block(a2t(ast), [])
        else:
            return node.Block(a2t(ast), [projectAST(e, s+1) for e in ast.block_items])

    elif isinstance(ast, c_ast.CompoundLiteral): #TODO [type*, init*]
        pass
    elif isinstance(ast, c_ast.Constant): # [type, value]
        if (ast.type == 'int'):
            return node.NumberI(a2t(ast), ast.value)
        elif (ast.type == 'float'):
            return node.NumberF(a2t(ast), ast.value)
        elif (ast.type == 'char'):
            ast.value = escapeString(ast.value)
            return node.NumberI(a2t(ast), int.from_bytes(ast.value[1].encode('utf-32be'), byteorder='big'))
        elif (ast.type == 'string'):
            ast.value = escapeString(ast.value)
            return node.String(a2t(ast), ast.value[1:-1])
        g.r.addReport(m.Report('fatal', a2t(ast), f"unsupported constant type '{ast.type}' for value '{ast.value}'"))

    elif isinstance(ast, c_ast.Continue): # []
        return node.Continue(a2t(ast))

    elif isinstance(ast, c_ast.Decl): # [name, quals, storage, funcspec, type*, init*, bitsize*]

        if type(ast.type) in (c_ast.TypeDecl, c_ast.PtrDecl, c_ast.ArrayDecl):
            init = projectAST(ast.init, s)
            if isinstance(init, node.String): # 初期化がstirngだった場合、リストに展開
                string = init.eval()
                li = list(map(lambda a : node.NumberI(a2t(ast), int.from_bytes(a.encode('utf-32be'), byteorder='big')), string))
                li.append(node.NumberI(a2t(ast), 0))
                init = li

            if (s == 0):
                return node.GlobalVar(a2t(ast), ast.name, projectAST(ast.type, s), init)
            else:
                return node.LocalVar(a2t(ast), ast.name, projectAST(ast.type, s), init)

        elif isinstance(ast.type, c_ast.FuncDecl): # 関数定義
            decl = projectAST(ast.type, s)
            return node.Func(a2t(ast), decl['type'].name, decl['type'], decl['args'], None)

        else:
            return projectAST(ast.type, s)

    elif isinstance(ast, c_ast.DeclList): #TODO [decls**]
        pass
    elif isinstance(ast, c_ast.Default): # [stmts**]
        return ['default', [projectAST(e, s+1) for e in ast.stmts]]

    elif isinstance(ast, c_ast.DoWhile): # [cond*, stmt*]
        return node.DoWhile(a2t(ast), projectAST(ast.stmt, s), projectAST(ast.cond, s))

    elif isinstance(ast, c_ast.EllipsisParam): #TODO []
        pass
    elif isinstance(ast, c_ast.EmptyStatement): #TODO []
        pass
    elif isinstance(ast, c_ast.Enum): # [name, values*]
        if ast.values is None: # is type define
            return m.Type(ast.name).setHint('enum')
        else: # is enum define
            return node.Enum(a2t(ast), ast.name, projectAST(ast.values, s))

    elif isinstance(ast, c_ast.Enumerator): # [name, value*]
        if ast.value is None:
            return (ast.name, None)
        else:
            if isinstance(ast.value, c_ast.Constant):
                return (ast.name, int(ast.value.value))
            elif isinstance(ast.value, c_ast.UnaryOp):
                return (ast.name, -int(ast.value.expr.value))
            else:
                g.r.addReport(m.Report('fatal', a2t(ast), f"enum must be \'int\'"))

    elif isinstance(ast, c_ast.EnumeratorList): # [enumerators**]
        itr = 0
        typ = m.Type('enum')
        for elem in ast.enumerators:
            tmp  = projectAST(elem, s)
            if tmp[1] is None:
                typ.addMember((tmp[0], itr))
                itr += 1
            else:
                typ.addMember(tmp)
                itr = tmp[1] + 1

        return typ

    elif isinstance(ast, c_ast.ExprList): #[exprs**]
        return [projectAST(e, s) for e in ast.exprs]

    elif isinstance(ast, c_ast.FileAST):
        return node.Program(a2t(ast), [projectAST(e, s) for e in ast.ext])

    elif isinstance(ast, c_ast.For): # [init*, cond*, next*, stmt*]
        return node.For(a2t(ast), projectAST(ast.init, s), projectAST(ast.cond, s), projectAST(ast.next, s), projectAST(ast.stmt, s))

    elif isinstance(ast, c_ast.FuncCall): # [name*, args*]
        return node.Funccall(a2t(ast), ast.name.name, projectAST(ast.args, s))

    elif isinstance(ast, c_ast.FuncDecl): # [args*, type*]
        return {"args": projectAST(ast.args, s) if ast.args is not None else [],
                "type": projectAST(ast.type, s)}

    elif isinstance(ast, c_ast.FuncDef): # [args*, type*]
        return projectAST(ast.decl, s).setBody(projectAST(ast.body, s))

    elif isinstance(ast, c_ast.Goto): # [name]
        return node.Goto(a2t(ast), ast.name)

    elif isinstance(ast, c_ast.ID): # [name]
        return node.Symbol(a2t(ast), ast.name)

    elif isinstance(ast, c_ast.IdentifierType):
        if len(ast.names) == 1:
            return  m.Type(ast.names[0])
        g.r.addReport(m.Report('fatal', a2t(ast), f"program error while processing IdentifierType"))

    elif isinstance(ast, c_ast.If): # [cond*, iftrue*, iffalse*]
        if ast.iffalse is None:
            return node.If(a2t(ast), projectAST(ast.cond, s), projectAST(ast.iftrue, s))
        else:
            return node.Ifelse(a2t(ast), projectAST(ast.cond, s), projectAST(ast.iftrue, s), projectAST(ast.iffalse, s))

    elif isinstance(ast, c_ast.InitList): # [exprs**]
        return [projectAST(e, s) for e in ast.exprs] #XXX

    elif isinstance(ast, c_ast.Label): # [name, stmt*]
        return node.Label(a2t(ast), ast.name, projectAST(ast.stmt))

    elif isinstance(ast, c_ast.NamedInitializer): #TODO [name**, expr*]
        pass
    elif isinstance(ast, c_ast.ParamList): # [params**]
        tmp = []
        for elem in ast.params:
            typ = projectAST(elem.type, s)
            tmp.append(m.Symbol(typ.name, typ))
        return tmp

    elif isinstance(ast, c_ast.PtrDecl):
        return projectAST(ast.type, s).addQuals(ast.quals).addRefcount(1)

    elif isinstance(ast, c_ast.Raw): # [type*, opc, arg, exprs**]
        return node.Raw(a2t(ast), projectAST(ast.type, s), ast.opc[1:-1], int(ast.arg.value), [projectAST(e, s) for e in ast.exprs])

    elif isinstance(ast, c_ast.Return): # [expr*]
        return node.Return(a2t(ast), projectAST(ast.expr, s))

    elif isinstance(ast, c_ast.Struct): # [name, decls**]
        if ast.decls is None:
            return m.Type(ast.name).setHint('struct')
        else:
            typ = m.Type('struct')
            for elem in ast.decls:
                typ.addMember((elem.name, projectAST(elem.type)))
            return node.Struct(a2t(ast), ast.name, typ)

    elif isinstance(ast, c_ast.StructRef): # [name*, type, filed*] type unused
        if ast.type == '.':
            return node.Indirect(a2t(ast), node.FieldAccess(a2t(ast), node.Address(a2t(ast), projectAST(ast.name, s)), ast.field.name))
        elif ast.type == '->':
            return node.Indirect(a2t(ast), node.FieldAccess(a2t(ast), projectAST(ast.name, s), ast.field.name))
        else:
            g.r.addReport(m.Report('fatal', a2t(ast), f"unsupported field access type '{ast.type}'"))

    elif isinstance(ast, c_ast.Switch): # [cond*, stmt*]
        return node.Switch(a2t(ast), projectAST(ast.cond, s), [projectAST(e, s+1) for e in ast.stmt.block_items])

    elif isinstance(ast, c_ast.TernaryOp): # [cond*, ifture*, iffalse*]
        return node.Ternary(a2t(ast), projectAST(ast.cond, s), projectAST(ast.iftrue, s), projectAST(ast.iffalse, s))

    elif isinstance(ast, c_ast.TypeDecl):
        typ = projectAST(ast.type, s)
        if isinstance(typ, m.Type):
            return typ.addQuals(ast.quals).setName(ast.declname)
        elif type(typ) in (node.Struct, node.Enum):
            return typ.typ
        else:
            return typ

    elif isinstance(ast, c_ast.Typedef): # [name, quals, storage, type*]
        typ = projectAST(ast.type, s)
        if isinstance(typ, node.Struct) or isinstance(typ, node.Enum):
            return node.Typedef(a2t(ast), ast.name, typ.typ.addQuals(ast.quals))
        else:
            return node.Typedef(a2t(ast), ast.name, typ.addQuals(ast.quals))

    elif isinstance(ast, c_ast.Typename): # [name, quals, type*]
        return projectAST(ast.type, s).addQuals(ast.quals)

    elif isinstance(ast, c_ast.UnaryOp): # [op, expr*]
        if ast.op == '!':
            return node.Inv(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == '+':
            return projectAST(ast.expr, s)
        elif ast.op == '-':
            return node.Minus(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == '++':
            return node.Pre_inc(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == '--':
            return node.Pre_dec(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == 'p++':
            return node.Post_inc(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == 'p--':
            return node.Post_dec(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == '*':
            return node.Indirect(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == '&':
            return node.Address(a2t(ast), projectAST(ast.expr, s))
        elif ast.op == 'sizeof':
            return node.Sizeof(a2t(ast), projectAST(ast.expr, s))
        else:
            g.r.addReport(m.Report('fatal', a2t(ast), f"unsupported unary op '{ast.op}'"))
            return

    elif isinstance(ast, c_ast.Union): #TODO [name, decls**]
        pass
    elif isinstance(ast, c_ast.While): # [cond*, stmt*]
        return node.While(a2t(ast), projectAST(ast.cond, s), projectAST(ast.stmt, s))

    elif isinstance(ast, c_ast.Pragma): #TODO [string]
        pass
    else:
        g.r.addReport(m.Report('fatal', a2t(ast), f"{type(ast)} is not listed!"))
        return

    g.r.addReport(m.Report('fatal', a2t(ast), f"{type(ast)} is not yet implemented!"))

def a2t(ast):
    if (ast is not None and ast.coord is not None):
        return m.TokenInfo(ast.coord.line, ast.coord.column, ast.coord.file)
    else:
        return m.TokenInfo(0, 0, '<ERROR>')


def makeAST(code):
    try:
        parser = CParser(lex_optimize=False, yacc_optimize=False)
        #parser = CParser()
        ast = parser.parse(code, filename=g.filename)
    except Exception as e:
        print(e)
        exit()

    #ast.show()

    node = projectAST(ast)

    #print(json.dumps(node, default=lambda x: {x.__class__.__name__: x.__dict__}, indent=2))
    #g.r.addReport(m.Report('fatal', a2t(ast), f"debugmode"))
    return node




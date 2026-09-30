import ast, math, operator, re
import tkinter as tk

BG, PANEL, NUM, FN, OPC, EQ, ACCENT = "#0f1120", "#171a2e", "#1f2340", "#2a2f55", "#6c5ce7", "#00d4a1", "#8b7cff"
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
FUNCS = {"±": lambda v: -v, "%": lambda v: v / 100, "1/x": lambda v: 1 / v, "x²": lambda v: v * v, "²√x": math.sqrt}
KEYS = [("%", "CE", "C", "⌫"), ("1/x", "x²", "²√x", "÷"), ("7", "8", "9", "×"),
        ("4", "5", "6", "−"), ("1", "2", "3", "+"), ("±", "0", ",", "=")]


def ev(node):  # evaluasi aman (tanpa eval)
    if isinstance(node, ast.Expression): return ev(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS: return OPS[type(node.op)](ev(node.left), ev(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -ev(node.operand)
    raise ValueError


def fmt(v): return str(int(v)) if v == int(v) else f"{v:.10g}"


def start(e):  # indeks awal angka terakhir (termasuk tanda minus)
    i = len(e)
    while i and e[i - 1] in "0123456789.": i -= 1
    return i - 1 if i and e[i - 1] == "-" else i


class Calc:
    def __init__(self): self.expr = self.hist = self.err = ""; self.done = False

    def cur(self):
        e = self.expr.rstrip("+−×÷")
        n = e[start(e):]
        return n if n.strip("-") else "0"

    def top(self):
        return self.hist if self.done else re.sub(r"\s*([+−×÷])\s*", r" \1 ", self.expr).strip()

    def press(self, k):
        e, self.err = self.expr, ""
        if k.isdigit() or k == ",":
            if self.done: e, self.done = "", False
            n = e[start(e):]
            if k == ",":
                if "." in n: return
                k = "." if n.strip("-") else "0."
            elif n.lstrip("-") == "0": e = e[:-1]
            e += k
        elif k in "+−×÷":
            self.done = False
            if not e: e = "-" if k == "−" else ""
            elif e[-1] in "+−×÷": e = e[:-1] + k
            elif e != "-": e += k
        elif k == "=":
            q = e.rstrip("+−×÷")
            if not q or q == "-": return
            try:
                r = fmt(ev(ast.parse(q.replace("×", "*").replace("÷", "/").replace("−", "-"), mode="eval")))
                self.hist, e, self.done = q + " =", r, True
            except ZeroDivisionError: self.err, e = "Tidak bisa bagi dengan 0", ""
            except (OverflowError, ValueError): self.err, e = "Hasil tidak valid", ""
        elif k == "C": e, self.hist, self.done = "", "", False
        elif k == "CE": e = "" if self.done else e[:start(e)]
        elif k == "⌫": e, self.done = e[:-1], False
        elif k in FUNCS:
            i = start(e)
            if e[i:].strip("-"):
                try: e = e[:i] + fmt(FUNCS[k](float(e[i:])))
                except ZeroDivisionError: self.err = "Tidak bisa bagi dengan 0"
                except ValueError: self.err = "Input tidak valid"
        self.expr = e


def lighten(c, a=.15):
    return "#%02x%02x%02x" % tuple(int(v + (255 - v) * a) for v in (int(c[i:i + 2], 16) for i in (1, 3, 5)))


class Btn(tk.Canvas):  # tombol membulat
    def __init__(self, master, text, cmd, bg, fg, font):
        super().__init__(master, bg=BG, highlightthickness=0, cursor="hand2")
        self.t, self.bg, self.fg, self.f, self.cmd, self.shape = text, bg, fg, font, cmd, None
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", lambda e: self.paint(lighten(bg)))
        self.bind("<Leave>", lambda e: self.paint(bg))
        self.bind("<ButtonPress-1>", lambda e: self.paint(lighten(bg, .35)))
        self.bind("<ButtonRelease-1>", self.release)

    def draw(self, e):
        self.delete("all")
        w, h, r = e.width - 1, e.height - 1, 18
        p = [r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h, w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0]
        self.shape = self.create_polygon(p, smooth=True, fill=self.bg, outline="")
        self.create_text(w / 2, h / 2, text=self.t, fill=self.fg, font=self.f)

    def paint(self, c):
        if self.shape: self.itemconfig(self.shape, fill=c)

    def release(self, e):
        self.paint(lighten(self.bg))
        if 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height(): self.cmd()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator"); self.geometry("340x590"); self.minsize(320, 540); self.configure(bg=BG)
        self.c = Calc()
        self.columnconfigure(0, weight=1); self.rowconfigure(2, weight=1)
        tk.Label(self, text="●  KALKULATOR", bg=BG, fg=ACCENT, font=("Segoe UI", 9, "bold")).grid(
            row=0, sticky="w", padx=20, pady=(14, 0))
        panel = tk.Frame(self, bg=PANEL, height=135); panel.pack_propagate(False)
        panel.grid(row=1, sticky="ew", padx=14, pady=10)
        self.top = tk.Label(panel, anchor="e", bg=PANEL, fg="#8b90b0", font=("Segoe UI", 11))
        self.main = tk.Label(panel, anchor="e", bg=PANEL, fg="white")
        self.top.pack(fill="x", padx=16, pady=(14, 0)); self.main.pack(fill="both", expand=True, padx=16)
        pad = tk.Frame(self, bg=BG); pad.grid(row=2, sticky="nsew", padx=9, pady=(0, 9))
        for i in range(4): pad.columnconfigure(i, weight=1, uniform="c")
        for r, row in enumerate(KEYS):
            pad.rowconfigure(r, weight=1, uniform="r")
            for i, k in enumerate(row):
                bg, fg = ((NUM, "white") if k.isdigit() or k == "," else (EQ, "#0b0d17") if k == "=" else
                          (OPC, "white") if k in "+−×÷" else (FN, "#aab4ff"))
                Btn(pad, k, lambda k=k: self.press(k), bg, fg, ("Segoe UI", 18 if k.isdigit() else 15, "bold")
                    ).grid(row=r, column=i, sticky="nsew", padx=5, pady=5)
        self.bind("<Key>", self.on_key)
        for s, k in (("<Return>", "="), ("<KP_Enter>", "="), ("<BackSpace>", "⌫"), ("<Escape>", "C"), ("<Delete>", "CE")):
            self.bind(s, lambda e, k=k: self.press(k))
        self.refresh()

    def on_key(self, e):
        k = {"-": "−", "*": "×", "/": "÷", ".": ","}.get(e.char, e.char)
        if e.char and (k.isdigit() or k in ",+−×÷%="): self.press(k)

    def press(self, k): self.c.press(k); self.refresh()

    def refresh(self):
        c = self.c
        t = c.err or c.cur().replace(".", ",")
        n = len(t)
        self.main.config(text=t, fg="#ff6b81" if c.err else "white",
                         font=("Segoe UI", 16 if c.err else 44 if n <= 10 else max(18, 44 - (n - 10) * 3), "bold"))
        self.top.config(text=c.top().replace(".", ",")[-32:])


if __name__ == "__main__":
    App().mainloop()

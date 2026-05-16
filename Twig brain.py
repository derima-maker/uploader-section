import socket, json, threading, time, os, ast, operator as op, random
import urllib.request, urllib.parse
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from datetime import datetime

# --- GLOBAL CONFIGURATION 2026 ---
API_KEY = "PLANFM-LOCAL-SECURE-2026"
HOST, PORT = '127.0.0.1', 65432
MEM_FILE = "brain_memory_2026.json"

# ==========================================
# PART 1: ACCURACY-WEIGHTED GENERATIVE ENGINE
# ==========================================

class GenerativeBrain:
    """A Scratch-Built Weighted Probability LLM (Markov Chain) for 2026."""
    def __init__(self):
        # Dictionary of weights: "Current Word": {"Next Word": Probability}
        self.weighted_chains = {
            "START": {"hello": 0.3, "hi": 0.3, "i": 0.2, "how": 0.2},
            "hello": {"i": 0.5, "how": 0.5},
            "hi": {"i": 0.5, "how": 0.5},
            "i": {"am": 0.8, "will": 0.2},
            "am": {"fine": 0.4, "good": 0.4, "doing": 0.2},
            "fine": {"and": 0.6, "thank": 0.3, "you": 0.1},
            "good": {"and": 0.6, "how": 0.4},
            "doing": {"well": 0.8, "ok": 0.2},
            "well": {"thank": 0.4, "and": 0.6},
            "how": {"are": 1.0},
            "are": {"you": 1.0},
            "you": {"?": 0.8, "too": 0.2},
            "and": {"you": 1.0},
            "thank": {"you": 1.0},
            "ok": {"and": 0.5, "?": 0.5}
        }

    def _weighted_pick(self, options_dict):
        """Standard-library 2026 weighted selection logic."""
        words = list(options_dict.keys())
        weights = list(options_dict.values())
        return random.choices(words, weights=weights, k=1)[0]

    def form_sentence(self, user_input):
        """Forms a sentence by traversing the highest probability word-paths."""
        words = []
        current_word = self._weighted_pick(self.weighted_chains["START"])
        words.append(current_word)

        # Build sentence chain (limit to 10 words for coherence)
        for _ in range(10):
            if current_word in self.weighted_chains:
                next_word = self._weighted_pick(self.weighted_chains[current_word])
                words.append(next_word)
                current_word = next_word
                if current_word == "?": break
            else: break
        
        sentence = " ".join(words).replace(" ?", "?")
        return sentence.capitalize()

# ==========================================
# PART 2: CORE BRAIN KERNEL SYSTEMS
# ==========================================

class CalculationEngine:
    def __init__(self):
        self.operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, 
                          ast.Pow: op.pow, ast.USub: op.neg, ast.Eq: op.eq, ast.Lt: op.lt, ast.Gt: op.gt}
    def evaluate(self, expr):
        try: return str(self._eval_node(ast.parse(expr, mode='eval').body))
        except: return "Logic Error"
    def _eval_node(self, node):
        if isinstance(node, ast.Constant): return node.value
        elif isinstance(node, ast.BinOp): return self.operators[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        elif isinstance(node, ast.UnaryOp): return self.operators[type(node.op)](self._eval_node(node.operand))
        return 0

class ResearchSystem:
    def __init__(self):
        self.base_url = "en.wikipedia.org"
    def fetch(self, title):
        params = urllib.parse.urlencode({'action':'query','prop':'extracts','exintro':True,'explaintext':True,'titles':title,'format':'json'})
        try:
            req = urllib.request.Request(f"{self.base_url}?{params}", headers={'User-Agent': 'PlanFM_Brain_2026'})
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode())
                pages = data['query']['pages']
                page_id = next(iter(pages))
                return pages[page_id].get('extract', 'Information not found.')
        except: return "Wikipedia Service Offline."

# ==========================================
# PART 3: THE KERNEL (SERVER)
# ==========================================

class BrainKernel:
    def __init__(self):
        self.storage = self.StorageSystem()
        self.logic_engine = CalculationEngine()
        self.research = ResearchSystem()
        self.gen_llm = GenerativeBrain()
        self.linked_apps = {} 
        self.router = self.LogicRouter(self)

    class StorageSystem:
        def __init__(self):
            self.memory = self.load()
            for key in ["vault", "external_registry", "audit_log"]:
                if key not in self.memory: self.memory[key] = {} if key != "audit_log" else []
        def load(self):
            if os.path.exists(MEM_FILE):
                with open(MEM_FILE,"r") as f: return json.load(f)
            return {"vault": {}, "external_registry": {}, "audit_log": []}
        def save(self):
            with open(MEM_FILE,"w") as f: json.dump(self.memory, f, indent=4)
        def log_activity(self, app_id, action):
            entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "app_id": app_id, "action": action}
            self.memory["audit_log"].insert(0, entry)
            if len(self.memory["audit_log"]) > 100: self.memory["audit_log"].pop()
            self.save()

    class LogicRouter:
        def __init__(self, kernel): self.kernel = kernel
        def route(self, request):
            rtype, payload = request.get("type"), request.get("payload")
            app_id = request.get("app_id", "Master_Dashboard")
            self.kernel.linked_apps[app_id] = datetime.now().strftime("%H:%M:%S")
            
            result = "Error"
            if rtype == "chat": result = self.kernel.gen_llm.form_sentence(payload)
            elif rtype == "store": self.kernel.storage.memory["vault"].update(payload); result = "Archived."
            elif rtype == "fetch_me": result = self.kernel.storage.memory["vault"].get(payload, "Not found.")
            elif rtype == "global_fetch":
                result = {"vault": self.kernel.storage.memory["vault"].get(payload), 
                          "external": self.kernel.storage.memory["external_registry"].get(payload)}
            elif rtype == "advanced_calc": result = self.kernel.logic_engine.evaluate(payload)
            elif rtype == "wiki_fetch": result = self.kernel.research.fetch(payload)
            elif rtype == "get_audit": result = self.kernel.storage.memory["audit_log"]
            elif rtype == "get_links": result = self.kernel.linked_apps

            self.kernel.storage.log_activity(app_id, f"{rtype}: {str(payload)[:30]}")
            return result

    def run_api(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT)); s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(32768).decode('utf-8')
                    if not data: continue
                    req = json.loads(data)
                    if req.get("api_key") == API_KEY:
                        resp = self.router.route(req)
                        conn.sendall(json.dumps({"status":"OK","data":resp}).encode('utf-8'))

# ==========================================
# PART 4: THE MASTER DASHBOARD (CLIENT)
# ==========================================

class PlanFMDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Plan F.M 2026 - Master Unified Hub")
        self.root.geometry("1100x850")
        self.root.configure(bg='#0a0a0a')

        # Real-Time Clock
        self.clock_lbl = tk.Label(root, text="", bg='#0a0a0a', fg='#00FFCC', font=("Consolas", 24, "bold"))
        self.clock_lbl.pack(pady=15)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab Setup
        self.setup_chat_tab()
        self.setup_retrieval_tab()
        self.setup_audit_tab()
        self.setup_logic_tab()
        self.setup_links_tab()

        self.update_clock(); self.auto_refresh()

    def setup_chat_tab(self):
        tab = tk.Frame(self.tabs, bg='#121212'); self.tabs.add(tab, text=" CHAT (GENERATIVE) ")
        self.chat_out = scrolledtext.ScrolledText(tab, height=20, bg='#000', fg='#8B00FF', font=("Arial", 11))
        self.chat_out.pack(fill='both', padx=20, pady=10)
        self.chat_in = tk.Entry(tab, bg='#222', fg='white', font=("Arial", 12))
        self.chat_in.pack(fill='x', padx=20, pady=5); self.chat_in.bind("<Return>", self.run_chat)

    def setup_retrieval_tab(self):
        tab = tk.Frame(self.tabs, bg='#121212'); self.tabs.add(tab, text=" GLOBAL RETRIEVAL ")
        self.search_in = tk.Entry(tab, bg='#222', fg='white'); self.search_in.pack(fill='x', padx=50, pady=10)
        self.search_out = scrolledtext.ScrolledText(tab, height=15, bg='#000', fg='#00FFCC'); self.search_out.pack(fill='both', padx=20)
        tk.Button(tab, text="RETRIEVE FROM BRAIN", command=self.run_retrieval, bg='#444', fg='white').pack(pady=5)

    def setup_audit_tab(self):
        tab = tk.Frame(self.tabs, bg='#121212'); self.tabs.add(tab, text=" SYSTEM AUDIT ")
        self.audit_tree = ttk.Treeview(tab, columns=("T", "A", "Act"), show='headings')
        self.audit_tree.heading("T", text="TIME"); self.audit_tree.heading("A", text="APP"); self.audit_tree.heading("Act", text="ACTION")
        self.audit_tree.pack(expand=True, fill='both')

    def setup_logic_tab(self):
        tab = tk.Frame(self.tabs, bg='#121212'); self.tabs.add(tab, text=" LOGIC / MATH ")
        self.logic_in = tk.Entry(tab, bg='#222', fg='white'); self.logic_in.pack(fill='x', padx=20, pady=10)
        self.logic_out = scrolledtext.ScrolledText(tab, height=10, bg='#000', fg='#00FFCC'); self.logic_out.pack(fill='both', padx=20)
        tk.Button(tab, text="COMPUTE", command=self.run_logic).pack()

    def setup_links_tab(self):
        tab = tk.Frame(self.tabs, bg='#121212'); self.tabs.add(tab, text=" CONNECTIONS ")
        self.links_tree = ttk.Treeview(tab, columns=("P", "S"), show='headings')
        self.links_tree.heading("P", text="PROGRAMME"); self.links_tree.heading("S", text="LAST SYNC")
        self.links_tree.pack(expand=True, fill='both')

    # --- Communication & UI Loops ---
    def call_api(self, rtype, payload):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2); s.connect((HOST, PORT))
                s.sendall(json.dumps({"api_key":API_KEY,"type":rtype,"payload":payload,"app_id":"Master_Hub"}).encode('utf-8'))
                return json.loads(s.recv(32768).decode('utf-8')).get("data", "Offline")
        except: return "Offline"

    def run_chat(self, e=None):
        txt = self.chat_in.get(); self.chat_in.delete(0, tk.END)
        self.chat_out.insert(tk.END, f"User: {txt}\n")
        res = self.call_api("chat", txt)
        self.chat_out.insert(tk.END, f"Plan F.M (LLM): {res}\n\n"); self.chat_out.see(tk.END)

    def run_retrieval(self):
        res = self.call_api("global_fetch", self.search_in.get())
        self.search_out.insert(tk.END, f"> {self.search_in.get()}\n{json.dumps(res, indent=2)}\n\n")

    def run_logic(self):
        res = self.call_api("advanced_calc", self.logic_in.get())
        self.logic_out.insert(tk.END, f"> {self.logic_in.get()}\nRes: {res}\n\n")

    def update_clock(self):
        self.clock_lbl.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def auto_refresh(self):
        links = self.call_api("get_links", ""); audit = self.call_api("get_audit", "")
        # Update Links
        for i in self.links_tree.get_children(): self.links_tree.delete(i)
        if isinstance(links, dict):
            for app, last in links.items(): self.links_tree.insert("", "end", values=(app, last))
        # Update Audit
        for i in self.audit_tree.get_children(): self.audit_tree.delete(i)
        if isinstance(audit, list):
            for entry in audit[:15]: self.audit_tree.insert("", "end", values=(entry['timestamp'], entry['app_id'], entry['action']))
        self.root.after(5000, self.auto_refresh)

if __name__ == "__main__":
    brain = BrainKernel(); threading.Thread(target=brain.run_api, daemon=True).start()
    root = tk.Tk(); app = PlanFMDashboard(root); root.mainloop()

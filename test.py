# import webview
# import platform
# from webview.menu import Menu, MenuAction, MenuSeparator


# # ============================================
# # DEMO 1 — Open a website in a desktop window
# # ============================================
# def demo_website():
#     window = webview.create_window(
#         title="PyWebview Demo — Website",
#         url="https://www.google.com",
#         width=1024,
#         height=768,
#         resizable=True,
#     )
#     webview.start()


# # ============================================
# # DEMO 2 — Load local HTML content
# # ============================================
# def demo_local_html():
#     html_content = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>PyWebview Local HTML</title>
#         <style>
#             * { margin: 0; padding: 0; box-sizing: border-box; }
#             body {
#                 font-family: 'Segoe UI', sans-serif;
#                 background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
#                 min-height: 100vh;
#                 display: flex;
#                 align-items: center;
#                 justify-content: center;
#                 color: white;
#             }
#             .card {
#                 background: rgba(255, 255, 255, 0.1);
#                 backdrop-filter: blur(10px);
#                 border: 1px solid rgba(255, 255, 255, 0.2);
#                 border-radius: 20px;
#                 padding: 40px;
#                 text-align: center;
#                 max-width: 500px;
#                 width: 90%;
#                 box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
#             }
#             .logo { font-size: 60px; margin-bottom: 20px; }
#             h1 { font-size: 28px; margin-bottom: 10px; color: #8a70ff; }
#             p { color: rgba(255,255,255,0.7); margin-bottom: 30px; line-height: 1.6; }
#             .badge {
#                 display: inline-block;
#                 background: #8a70ff;
#                 color: white;
#                 padding: 6px 16px;
#                 border-radius: 20px;
#                 font-size: 13px;
#                 margin: 4px;
#             }
#             .btn {
#                 display: inline-block;
#                 margin-top: 24px;
#                 padding: 12px 32px;
#                 background: #8a70ff;
#                 color: white;
#                 border: none;
#                 border-radius: 10px;
#                 font-size: 16px;
#                 cursor: pointer;
#                 transition: background 0.2s;
#             }
#             .btn:hover { background: #6f5cff; }
#             .counter {
#                 font-size: 48px;
#                 font-weight: bold;
#                 color: #8a70ff;
#                 margin: 20px 0;
#             }
#         </style>
#     </head>
#     <body>
#         <div class="card">
#             <div class="logo"></div>
#             <h1>PyWebview is Working!</h1>
#             <p>
#                 This is a native desktop window powered by
#                 PyWebview running on your Kali Linux machine.
#             </p>
#             <div>
#                 <span class="badge">Python</span>
#                 <span class="badge">PyWebview</span>
#                 <span class="badge">HTML</span>
#                 <span class="badge">CSS</span>
#                 <span class="badge">JavaScript</span>
#             </div>
#             <div class="counter" id="counter">0</div>
#             <button class="btn" onclick="increment()">Click Me!</button>
#             <script>
#                 let count = 0;
#                 function increment() {
#                     count++;
#                     document.getElementById('counter').textContent = count;
#                 }
#                 setInterval(() => {
#                     const now = new Date();
#                     document.title = 'PyWebview — ' + now.toLocaleTimeString();
#                 }, 1000);
#             </script>
#         </div>
#     </body>
#     </html>
#     """
#     window = webview.create_window(
#         title="PyWebview Demo — Local HTML",
#         html=html_content,
#         width=700,
#         height=600,
#         resizable=True,
#         background_color="#1a1a2e",
#     )
#     webview.start()


# # ============================================
# # DEMO 3 — Python talking to JavaScript
# # ============================================
# class Api:
#     """Python functions exposed to JavaScript"""

#     def get_message(self):
#         return "Hello from Python!"

#     def add_numbers(self, a, b):
#         return f"{a} + {b} = {a + b}"

#     def get_system_info(self):
#         return {
#             "os": platform.system(),
#             "version": platform.version(),
#             "machine": platform.machine(),
#             "python": platform.python_version(),
#         }


# # ============================================
# # MENU ACTION FUNCTIONS
# # ============================================
# def on_new(window):
#     window.load_html("""
#         <div style='
#             font-family: Segoe UI, sans-serif;
#             background: #12121f;
#             color: white;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             height: 100vh;
#             text-align: center;
#         '>
#             <div>
#                 <div style='font-size:60px'></div>
#                 <h1 style='color:#8a70ff;margin:16px 0'>New Page Loaded!</h1>
#                 <p style='color:#9a9ab3'>This was triggered from the File menu</p>
#             </div>
#         </div>
#     """)


# def on_zoom_in(window):
#     window.evaluate_js(
#         "document.body.style.zoom = (parseFloat(document.body.style.zoom) || 1) + 0.1"
#     )


# def on_zoom_out(window):
#     window.evaluate_js(
#         "document.body.style.zoom = (parseFloat(document.body.style.zoom) || 1) - 0.1"
#     )


# def on_zoom_reset(window):
#     window.evaluate_js("document.body.style.zoom = 1")


# def on_about(window):
#     window.load_html(f"""
#         <div style='
#             font-family: Segoe UI, sans-serif;
#             background: #12121f;
#             color: white;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             height: 100vh;
#             text-align: center;
#         '>
#             <div>
#                 <div style='font-size:60px'></div>
#                 <h1 style='color:#8a70ff;margin:16px 0'>PyWebview Demo</h1>
#                 <p style='color:#9a9ab3'>Version 1.0.0</p>
#                 <p style='color:#9a9ab3;margin-top:8px'>Built with Python + PyWebview</p>
#                 <p style='color:#9a9ab3;margin-top:8px'>
#                     OS: {platform.system()} |
#                     Machine: {platform.machine()} |
#                     Python: {platform.python_version()}
#                 </p>
#             </div>
#         </div>
#     """)


# def on_toggle_fullscreen(window):
#     window.toggle_fullscreen()


# def on_quit(window):
#     window.destroy()


# # ============================================
# # DEMO 4 — With Native Menu
# # ============================================
# def demo_with_menu():
#     api = Api()

#     html_content = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             * { margin: 0; padding: 0; box-sizing: border-box; }
#             body {
#                 font-family: 'Segoe UI', sans-serif;
#                 background: #12121f;
#                 color: white;
#                 padding: 30px;
#             }
#             h1 { color: #8a70ff; margin-bottom: 8px; font-size: 24px; }
#             .subtitle { color: #9a9ab3; margin-bottom: 24px; font-size: 14px; }
#             .section {
#                 background: #1c1c2d;
#                 border: 1px solid #2d2d44;
#                 border-radius: 12px;
#                 padding: 20px;
#                 margin-bottom: 20px;
#             }
#             .section h3 { color: #8a70ff; margin-bottom: 12px; font-size: 16px; }
#             .btn {
#                 padding: 10px 20px;
#                 background: #8a70ff;
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 cursor: pointer;
#                 font-size: 14px;
#                 margin-right: 8px;
#                 margin-bottom: 8px;
#                 transition: background 0.2s;
#             }
#             .btn:hover { background: #6f5cff; }
#             .result {
#                 margin-top: 12px;
#                 padding: 12px;
#                 background: #12121f;
#                 border-radius: 8px;
#                 color: #2ecc71;
#                 font-family: monospace;
#                 font-size: 14px;
#                 min-height: 40px;
#             }
#             input {
#                 padding: 8px 12px;
#                 background: #12121f;
#                 border: 1px solid #2d2d44;
#                 border-radius: 8px;
#                 color: white;
#                 font-size: 14px;
#                 width: 80px;
#                 margin-right: 8px;
#             }
#             .tip {
#                 background: #1c1c2d;
#                 border-left: 3px solid #8a70ff;
#                 padding: 12px 16px;
#                 border-radius: 0 8px 8px 0;
#                 color: #9a9ab3;
#                 font-size: 13px;
#                 margin-bottom: 20px;
#             }
#         </style>
#     </head>
#     <body>
#         <h1> Python ↔ JavaScript Bridge</h1>
#         <p class="subtitle">With Native OS Menu — check the menu bar above!</p>

#         <div class="tip">
#             Try the menu bar:
#             <strong>File → New</strong> |
#             <strong>View → Zoom In/Out</strong> |
#             <strong>Help → About</strong>
#         </div>

#         <div class="section">
#             <h3>1. Call Python function from JavaScript</h3>
#             <button class="btn" onclick="getMessage()">
#                 Get Python Message
#             </button>
#             <div class="result" id="result1">Click the button...</div>
#         </div>

#         <div class="section">
#             <h3>2. Send data to Python and get result back</h3>
#             <input type="number" id="num1" value="10" />
#             <span style="color:#8a70ff">+</span>
#             <input type="number" id="num2" value="25" />
#             <button class="btn" onclick="addNumbers()">Calculate</button>
#             <div class="result" id="result2">Enter numbers above...</div>
#         </div>

#         <div class="section">
#             <h3>3. Get system info from Python</h3>
#             <button class="btn" onclick="getSystemInfo()">
#                 Get System Info
#             </button>
#             <div class="result" id="result3">Click to get info...</div>
#         </div>

#         <script>
#             async function getMessage() {
#                 const result = await window.pywebview.api.get_message();
#                 document.getElementById('result1').textContent = result;
#             }
#             async function addNumbers() {
#                 const a = parseInt(document.getElementById('num1').value);
#                 const b = parseInt(document.getElementById('num2').value);
#                 const result = await window.pywebview.api.add_numbers(a, b);
#                 document.getElementById('result2').textContent = result;
#             }
#             async function getSystemInfo() {
#                 const info = await window.pywebview.api.get_system_info();
#                 document.getElementById('result3').textContent =
#                     `OS: ${info.os} | Machine: ${info.machine} | Python: ${info.python}`;
#             }
#         </script>
#     </body>
#     </html>
#     """

#     window = webview.create_window(
#         title="PyWebview Demo — Python ↔ JS Bridge + Menu",
#         html=html_content,
#         width=800,
#         height=700,
#         js_api=api,
#         resizable=True,
#         background_color="#12121f",
#     )

#     # ============================================
#     # NATIVE MENU — positional args for pywebview 6.x
#     # ============================================
#     menu = [
#         Menu("File", [
#             MenuAction("New", lambda: on_new(window)),
#             MenuSeparator(),
#             MenuAction("Toggle Fullscreen", lambda: on_toggle_fullscreen(window)),
#             MenuSeparator(),
#             MenuAction("Quit", lambda: on_quit(window)),
#         ]),
#         Menu("View", [
#             MenuAction("Zoom In", lambda: on_zoom_in(window)),
#             MenuAction("Zoom Out", lambda: on_zoom_out(window)),
#             MenuAction("Reset Zoom", lambda: on_zoom_reset(window)),
#         ]),
#         Menu("Help", [
#             MenuAction("About", lambda: on_about(window)),
#         ]),
#     ]

#     webview.start(menu=menu)


# # ============================================
# # RUN
# # ============================================
# if __name__ == "__main__":
#     # Try one at a time — comment/uncomment to switch

#     # demo_website()           # DEMO 1 — loads google.com
#     # demo_local_html()        # DEMO 2 — local HTML with counter
#     # demo_python_js_bridge()  # DEMO 3 — Python ↔ JS bridge
#     demo_with_menu()           # DEMO 4 — With native OS menu
from inkos.app.base import App
from inkos.events import ACTION_BACK
from inkos.services.http_request import Response


class ScreensaverApp(App):
    app_id = "system.screensaver"
    name = "屏保"
    permissions = ("screensaver",)

    def on_start(self):
        self.context.http.route("/app/system.screensaver", self._http_config)

    def on_event(self, event):
        if event.action == ACTION_BACK:
            self.context.exit_app()

    def render(self, display):
        if self.context.kernel.sleeping:
            self._render_screensaver(display)
        else:
            display.line("屏保")
            display.line("请在网页配置")
            display.line("/app/system.screensaver")

    def _render_screensaver(self, display):
        mode = self.context.settings.get("screensaver.mode", "text")
        if mode == "image":
            data = self._hex_to_bytes(self.context.settings.get("screensaver.image_hex", ""))
            if data:
                display.bitmap_1bit(0, 0, display.width, display.height, data)
                return
        title = self.context.settings.get("screensaver.title", "InkOS")
        subtitle = self.context.settings.get("screensaver.subtitle", "休眠中")
        display.set_line_y(32)
        display.line(title)
        display.line(subtitle)

    def _http_config(self, request, conn=None):
        if request.method == "POST":
            mode = request.form("mode", "text")
            self.context.settings.set("screensaver.mode", mode)
            self.context.settings.set("screensaver.title", request.form("title", "InkOS"))
            self.context.settings.set("screensaver.subtitle", request.form("subtitle", "休眠中"))
            image_hex = request.form("image_hex", "")
            if image_hex:
                self.context.settings.set("screensaver.image_hex", image_hex)
            return Response.redirect("/app/system.screensaver")

        mode = self.context.settings.get("screensaver.mode", "text")
        title = self.context.settings.get("screensaver.title", "InkOS")
        subtitle = self.context.settings.get("screensaver.subtitle", "休眠中")
        page = self._page(mode, title, subtitle)
        return Response.html(self.context.http.page(page))

    def _page(self, mode, title, subtitle):
        checked_text = "checked" if mode == "text" else ""
        checked_image = "checked" if mode == "image" else ""
        title = self._html_escape(title)
        subtitle = self._html_escape(subtitle)
        return """<main><h2>Screensaver</h2>
<section class='card'><form method='post' id='form'>
<label><input type='radio' name='mode' value='text' %s> Text</label>
<label><input type='radio' name='mode' value='image' %s> Image</label>
<label>Title</label><input name='title' value='%s'>
<label>Subtitle</label><input name='subtitle' value='%s'>
<label>Image</label><input type='file' id='img' accept='image/*'>
<canvas id='cv' width='212' height='104' style='width:100%%;border:1px solid #ccc'></canvas>
<input type='hidden' name='image_hex' id='hex'>
<button>Save</button></form></section>
<script>
const img=document.getElementById('img'),cv=document.getElementById('cv'),ctx=cv.getContext('2d'),hex=document.getElementById('hex');
img.onchange=()=>{const f=img.files[0]; if(!f)return; const im=new Image();
im.onload=()=>{let t=document.createElement('canvas'),tc=t.getContext('2d'),rot=im.height>im.width;t.width=rot?im.height:im.width;t.height=rot?im.width:im.height;
if(rot){tc.translate(t.width,0);tc.rotate(Math.PI/2)}tc.drawImage(im,0,0);ctx.fillStyle='white';ctx.fillRect(0,0,212,104);let s=Math.min(212/t.width,104/t.height),w=t.width*s,h=t.height*s,x=(212-w)/2,y=(104-h)/2;ctx.drawImage(t,x,y,w,h);
let imgd=ctx.getImageData(0,0,212,104),d=imgd.data,gray=new Array(212*104);
for(let i=0;i<gray.length;i++){let p=i*4;gray[i]=0.299*d[p]+0.587*d[p+1]+0.114*d[p+2]}
for(let y0=0;y0<104;y0++){for(let x0=0;x0<212;x0++){let i=y0*212+x0,old=gray[i],nw=old<128?0:255,er=old-nw;gray[i]=nw;if(x0+1<212)gray[i+1]+=er*7/16;if(y0+1<104){if(x0>0)gray[i+211]+=er*3/16;gray[i+212]+=er*5/16;if(x0+1<212)gray[i+213]+=er/16}}}
let out='';for(let yy=0;yy<104;yy++){for(let bx=0;bx<27;bx++){let b=0;for(let bit=0;bit<8;bit++){let xx=bx*8+bit;if(xx<212){let i=yy*212+xx,p=i*4;if(gray[i]<128){b|=(128>>bit);d[p]=d[p+1]=d[p+2]=0}else{d[p]=d[p+1]=d[p+2]=255}d[p+3]=255}}out+=('0'+b.toString(16)).slice(-2)}}ctx.putImageData(imgd,0,0);hex.value=out;document.querySelector('input[value=image]').checked=true};
im.src=URL.createObjectURL(f)}
</script></main>""" % (checked_text, checked_image, title, subtitle)

    def _html_escape(self, value):
        return str(value).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    def _hex_to_bytes(self, text):
        if not text:
            return None
        try:
            data = bytearray()
            for i in range(0, len(text), 2):
                data.append(int(text[i:i + 2], 16))
            return data
        except Exception:
            return None


def create_app(context):
    return ScreensaverApp(context)

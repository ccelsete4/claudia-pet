// Sprite sheet loading, playback, and canvas transitions.
function sheetPlace(cv, dpr) {
  const b = $('body'), S = b.offsetHeight * 638 / 640 / SHEET.charH   // 静态待机立绘里人物约占立绘高的 638/640
  const w = SHEET.w * S, h = SHEET.h * S
  cv.style.width = w + 'px'; cv.style.height = h + 'px'
  cv.style.left = (b.offsetWidth / 2 - SHEET.centerX * S) + 'px'
  cv.style.top = (b.offsetHeight - SHEET.feetY * S) + 'px'
  const W = Math.max(1, Math.round(w * dpr)), H = Math.max(1, Math.round(h * dpr))
  if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H }
}
function sheetDraw(s = sheet) {
  if (!s?.img) return
  const dpr = window.devicePixelRatio || 1
  if (s.layoutVersion !== sheetLayoutVersion || s.dpr !== dpr) {
    sheetPlace(s.canvas, dpr)
    s.layoutVersion = sheetLayoutVersion
    s.dpr = dpr
  }
  const ctx = s.canvas.getContext('2d'), c = s.frame % SHEET.cols, r = Math.floor(s.frame / SHEET.cols)
  const w = s.img.width / SHEET.cols, h = SHEET.h * w / SHEET.w
  ctx.clearRect(0, 0, s.canvas.width, s.canvas.height)
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(s.img, c * w, r * h, w, h, 0, 0, s.canvas.width, s.canvas.height)
}
function sheetCanAdvance(s) {
  return !!s?.img && (s.frame < s.to || !!s.hold || s.loop || !!s.cycle && s.frame >= s.cycle[1])
}
function sheetStep(s) {
  if (s.holding) {   // 来回播，没有接缝
    if (s.frame >= s.hold[1]) s.dir = -1; else if (s.frame <= s.hold[0]) s.dir = 1
    s.frame += s.dir
  } else if (s.cycle && s.frame >= s.cycle[1]) s.frame = s.cycle[0]   // 走路的步伐循环
  else if (s.frame < s.to) s.frame++
  else if (s.hold) { s.holding = true; s.dir = -1; s.frame-- }
  else s.frame = s.from
}
function sheetTick() {
  const s = sheet
  if (pageHidden || !sheetCanAdvance(s)) return
  auraPulse()   // 和这一帧一起出，不多出一帧
  sheetStep(s)
  sheetDraw()
  if (s.cycle && !s.cycled && s.frame >= s.cycle[0]) { s.cycled = true; s.onCycle?.() }   // 起步动作演完、开始迈步
  if (sheet === s && !sheetCanAdvance(s)) updateAnimationTimers()
}
// still：这个姿态的静态图。动画淡入、静态图淡出之后，把底下藏着的静态图换成它，动画停下时露出来的是对的那张
// a.keepUrl：接着演正在播的这一张（走路收尾、离场动作），不另抽一张
function playSheet(a, still, key = null) {
  const from = a.from ?? 0
  const url = a.keepUrl && sheet?.url && a.urls.includes(sheet.url) ? sheet.url : pick(a.urls)
  const name = a.sheets?.find(n => char()?.sheets?.[n] === url)
  const preview = name && char()?.sheets?.[name + '.scaled']
  const asset = preview && fitsScaledSheet() ? preview : url
  const s = { key, url, asset, from, to: a.to ?? SHEET.frames - 1, hold: a.hold, loop: !!a.loop, cycle: a.cycle, cycled: false, onCycle: null,
    frame: from, dir: 1, holding: false,
    canvas: sheetCanvases.find(c => c !== sheetFront), img: null, timer: null }
  // 还是正在播的这张图（已经解码好）：沿用这块画布和这份图，直接跳到新的起点接着播。
  // 原来每次都重新读、重新解码（约 0.3 秒，画面停在半路）再交叉淡入，走路收尾、睡醒、收起零食、点击重播时看着是卡一下、叠个重影再换掉（2026-11-07 用户反馈向左跑收尾生硬）
  const prev = sheet
  if (prev?.img && prev.asset === asset && prev.key === key && sheetFront === prev.canvas && !prev.cancelLoad) {
    clearInterval(prev.timer); prev.cancelLoad?.()
    Object.assign(s, { canvas: prev.canvas, img: prev.img, layoutVersion: prev.layoutVersion, dpr: prev.dpr })
    prev.img = null   // 交给新的这份，别在 disposeSheet 里关掉
    sheet = s
    clearTimeout(sheetReleaseTimer)
    sheetDraw()
    updateAnimationTimers()
    if (still) setTimeout(() => { if (sheet === s) showImage(still, true) }, 450)
    return
  }
  // 换成另一张图：新图解码（约 0.3 秒）和交叉淡入的这段时间，旧动画接着往下播（原来停在半路不动，换动作时先定格一下）
  if (prev?.img && sheetFront === prev.canvas) fadeOut(prev)
  else disposeSheet()
  if (fading && fading.canvas === s.canvas) endFade()   // 新图要画到这块画布上：淡出的那个先停
  sheet = s
  updateAnimationTimers()
  clearTimeout(sheetReleaseTimer)
  const loaded = img => {
    if (sheet !== s) { img.close?.(); return }
    s.cancelLoad = null
    s.img = img
    sheetDraw()
    const old = sheetFront
    s.canvas.classList.add('on'); if (old && old !== s.canvas) old.classList.remove('on')
    sheetFront = s.canvas
    document.documentElement.classList.add('sheet-on')
    updateAnimationTimers()
    upgradeScaledSheet()
    if (still) setTimeout(() => { if (sheet === s) showImage(still, true) }, 450)
    if (old && old !== s.canvas) setTimeout(() => { if (sheetFront !== old) { endFade(old); old.width = 1; old.height = 1 } }, 450)   // 淡出后放掉旧画布
    setTimeout(() => { if (fading && fading.canvas !== sheetFront) endFade() }, 450)   // 不管从哪来的，淡出完就停
  }
  const failed = () => {
    if (sheet !== s) return
    window.chrome?.webview?.postMessage({ imageError: s.url })
    // 读不到：不退回静态立绘，改播待机动画（只试一次，待机本身也读不到就停在原来的画面）
    const idle = !s.fallback && anim('idle')
    if (idle && idle.urls.some(u => u !== s.url)) { const k = { ...idle, urls: idle.urls.filter(u => u !== s.url) }; playSheet(k, null); sheet.fallback = true; return }
    stopSheet()
  }
  s.cancelLoad = loadSheet(s.asset, loaded, s.asset === s.url ? failed : () => {
    if (sheet !== s) return
    s.asset = s.url
    s.cancelLoad = loadSheet(s.url, loaded, failed)
  })
}

// Scaled sheets have 448×252 pixels per frame. Keep full resolution whenever the
// physical canvas needs more pixels, including when a visible clip is enlarged.
function fitsScaledSheet() {
  const w = $('body').offsetHeight * (638 / 640) / SHEET.charH * SHEET.w
  return Math.round(w * (window.devicePixelRatio || 1)) <= 448
}
function upgradeScaledSheet() {
  const s = sheet
  if (!s?.img || s.asset === s.url || s.cancelLoad || fitsScaledSheet()) return
  s.cancelLoad = loadSheet(s.url, img => {
    if (sheet !== s) { img.close?.(); return }
    s.cancelLoad = null
    s.img.close?.()
    s.img = img
    s.asset = s.url
    sheetDraw(s)
  }, () => { if (sheet === s) s.cancelLoad = null })
}
// 读一张精灵图交给 done（ImageBitmap 或 <img>，都能 drawImage）；读不到调 fail。
// 每张 5120×5400，解码一张约 0.3 秒：用 <img> 时解码发生在第一次画上画布的时候，网页帧循环整个停住约 0.3 秒
// （实测 290–345 ms，拖动起步换「被拎起来」时会顿一下）。先 fetch 成 Blob 再 createImageBitmap，解码在后台线程，
// 主线程只剩第一次画时约 75 ms 的上传（2026-11-06）。画出来的像素一样。
// 拿不到时退回 <img>：测试里的 file:// 地址、读失败、4 秒还没解完（页面在后台时解码可能一直不返回，所以 <img> 也只用 onload 不用 decode()）
function loadSheet(url, done, fail) {
  const controller = new AbortController()
  const { signal } = controller
  let timer = null, img = null, blob = null, objectUrl = null
  const releaseUrl = () => {
    if (objectUrl) URL.revokeObjectURL(objectUrl)
    objectUrl = null
  }
  const viaImg = () => {
    if (signal.aborted) return
    clearTimeout(timer)
    controller.abort()
    if (blob) objectUrl = URL.createObjectURL(blob)
    blob = null
    img = new Image()
    img.onload = () => { releaseUrl(); done(img) }
    img.onerror = () => { releaseUrl(); fail() }
    img.src = objectUrl || url
  }
  if (window.createImageBitmap && /^https:/.test(url)) {
    timer = setTimeout(viaImg, 4000)
    fetch(url, { signal })
      .then(r => {
        if (!r.ok) throw new Error(r.status)
        return r.blob()
      })
      .then(data => {
        if (signal.aborted) return
        blob = data
        return createImageBitmap(data)
      })
      .then(bitmap => {
        clearTimeout(timer)
        if (!bitmap) return
        if (signal.aborted) bitmap.close()
        else done(bitmap)
      }, viaImg)
  } else viaImg()
  return () => {
    clearTimeout(timer)
    controller.abort()
    if (img) {
      img.onload = img.onerror = null
      img.removeAttribute('src')
    }
    releaseUrl()
  }
}
// 正在淡出的旧动画：单独按 12 帧接着播，淡出完（或者又换了别的）再停、放掉它的图
let fading = null
function fadeOut(s) {
  endFade()
  clearInterval(s.timer); s.timer = null; s.cancelLoad?.()
  fading = s
  s.fadeTimer = setInterval(() => { if (!pageHidden && sheetCanAdvance(s)) { sheetStep(s); sheetDraw(s) } }, 1000 / SHEET.fps)
}
function endFade(canvas = null) {
  const f = fading
  if (!f || (canvas && f.canvas !== canvas)) return
  fading = null; clearInterval(f.fadeTimer); f.img?.close?.(); f.img = null
}
function disposeSheet() {
  if (!sheet) return
  clearInterval(sheet.timer)
  sheet.cancelLoad?.()
  sheet.img?.close?.()
  sheet = null
}
function stopSheet() {
  if (sheet?.img && sheetFront === sheet.canvas) { fadeOut(sheet); sheet = null }   // 淡出时接着播，不停在半路
  else disposeSheet()
  updateAnimationTimers()
  if (!sheetFront && !document.documentElement.classList.contains('sheet-on')) return
  for (const c of sheetCanvases) c.classList.remove('on')
  sheetFront = null
  document.documentElement.classList.remove('sheet-on')
  clearTimeout(sheetReleaseTimer)
  sheetReleaseTimer = setTimeout(() => { if (!sheet) { endFade(); for (const c of sheetCanvases) { c.width = 1; c.height = 1 } } }, 450)
}

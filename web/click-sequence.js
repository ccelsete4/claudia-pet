;(function(root) {
  class ClickSequence {
    constructor(visual, active) { this.visual = visual; this.active = active; this.token = 0; this.cancelVisual = null }
    get busy() { return this.cancelVisual !== null }
    play(action, enabled) {
      if (!enabled) { this.cancel(); action(); return }
      this.cancelVisual?.()
      const token = ++this.token
      this.active(true)
      this.cancelVisual = this.visual(() => {
        if (token !== this.token) return
        this.cancelVisual = null
        this.active(false)
      })
      action()
    }
    cancel() {
      ++this.token; this.cancelVisual?.(); this.cancelVisual = null; this.active(false)
    }
  }
  root.ClickSequence = ClickSequence
  if (typeof module !== 'undefined') module.exports = ClickSequence
})(typeof window !== 'undefined' ? window : globalThis)

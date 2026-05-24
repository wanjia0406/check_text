/** Escape text for safe ``v-html`` insertion (user document + error snippets). */
export function escapeHtml(text) {
  if (!text) return "";
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

/** Regex-escape a literal substring for ``RegExp`` construction. */
export function escapeRegExp(s) {
  return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Collect non-overlapping matches for multiple needles in ``text``.
 * ``pickInfo`` chooses which metadata object to attach when duplicates exist.
 */
export function collectNonOverlappingMatches(text, needleToInfo) {
  const matches = [];
  Object.keys(needleToInfo).forEach((errorText) => {
    if (!errorText) return;
    const regex = new RegExp(escapeRegExp(errorText), "g");
    let match;
    let hasMatch = false;
    while ((match = regex.exec(text)) !== null) {
      hasMatch = true;
      matches.push({
        start: match.index,
        end: match.index + errorText.length,
        text: errorText,
        info: needleToInfo[errorText],
      });
    }
    if (!hasMatch) {
      matches.push({ start: -1, end: -1, text: errorText, info: needleToInfo[errorText], unmatched: true });
    }
  });

  const positioned = matches.filter((m) => m.start >= 0).sort((a, b) => a.start - b.start);
  const merged = [];
  positioned.forEach((m) => {
    if (merged.length === 0) {
      merged.push(m);
      return;
    }
    const last = merged[merged.length - 1];
    if (m.start < last.end) {
      if (m.end > last.end) last.end = m.end;
    } else {
      merged.push(m);
    }
  });
  const unmatched = matches.filter((m) => m.unmatched).map((m) => m.info);
  return { merged, unmatched };
}

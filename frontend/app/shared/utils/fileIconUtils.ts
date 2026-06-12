export const getFileIcon = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const iconMap: Record<string, string> = {
    pdf: 'lucide:file-text',
    doc: 'lucide:file-text',
    docx: 'lucide:file-text',
    txt: 'lucide:file-text',
    xls: 'lucide:file-spreadsheet',
    xlsx: 'lucide:file-spreadsheet',
    csv: 'lucide:file-spreadsheet',
    ppt: 'lucide:file-presentation',
    pptx: 'lucide:file-presentation',
    zip: 'lucide:archive',
    rar: 'lucide:archive',
    '7z': 'lucide:archive',
    jpg: 'lucide:image',
    jpeg: 'lucide:image',
    png: 'lucide:image',
    gif: 'lucide:image',
    svg: 'lucide:image',
    webp: 'lucide:image',
    mp4: 'lucide:video',
    avi: 'lucide:video',
    mov: 'lucide:video',
    mp3: 'lucide:music',
    wav: 'lucide:music',
    code: 'lucide:code',
    js: 'lucide:code',
    ts: 'lucide:code',
    vue: 'lucide:code',
    json: 'lucide:code',
  }
  return iconMap[ext] || 'lucide:file'
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

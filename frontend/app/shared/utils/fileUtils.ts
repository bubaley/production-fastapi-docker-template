import type { FetchResponse } from 'ofetch'


export const downloadFileFromResponse = async (response: FetchResponse<Blob | ArrayBuffer>) => {
  const disposition = response.headers.get('content-disposition')
  let filename = 'download.txt'

  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/)
    if (match && match[1]) {
      filename = decodeURIComponent(match[1])
    }
  }
  if (response._data instanceof Blob) {
    downloadFile(new Blob([response._data || '']), filename)
  } else if (response._data instanceof ArrayBuffer) {
    const downloadBlob = new Blob([response._data], { type: 'application/octet-stream' })
    downloadFile(downloadBlob, filename)
  }

}

export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export const initUploadFile = (config: { accept?: string[]; multiple?: boolean; handler: (files: FileList) => void }) => {
  const input = document.createElement('input')
  input.setAttribute('hidden', 'true')
  input.setAttribute('type', 'file')
  input.setAttribute('id', (Math.random() + 1).toString(36).substring(7))
  if (config.accept) input.setAttribute('accept', config.accept.join(', '))
  if (config.multiple) input.setAttribute('multiple', 'true')
  document.body.appendChild(input)
  input.click()
  input.addEventListener('change', (e) => {
    const input = e.target as HTMLInputElement
    if (input && input.files && input.files.length) {
      config.handler(input.files)
      input.remove()
    } else if (input) {
      input.remove()
    }
  })
}

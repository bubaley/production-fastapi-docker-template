import type { $Fetch, FetchResponse, MappedResponseType, ResponseType } from 'ofetch'

export interface AppApiSendConfig {
  method?: 'get' | 'post' | 'put' | 'delete'
  resource?: string // override base resource
  action?: string
  data?: Record<string, unknown>
  params?: Record<string, unknown>
  headers?: Record<string, string>
  id?: string | number | null
  absoluteUrl?: string // override full url
}

export type AppApiSendConfigRaw<R extends ResponseType> = AppApiSendConfig & {
  responseType?: R
}

export class AppApi {
  _client: $Fetch
  resource: string

  constructor(raw: { resource: string; client: $Fetch }) {
    this.resource = raw.resource
    this._client = raw.client
  }

  async sendRaw<T, R extends ResponseType = "json">(data: AppApiSendConfigRaw<R>): Promise<FetchResponse<MappedResponseType<R, T>>> {
    const requestData: any = this.getRequestData(data)
    requestData.responseType = data.responseType
    return await this._client.raw<T, R>(this.buildUrl(data), requestData)
  }

  async send<T>(data: AppApiSendConfig) {
    return await this._client<T>(this.buildUrl(data), this.getRequestData(data))
  }

  getRequestData(data: AppApiSendConfig) {
    return {
      method: data.method || 'get',
      body: data.data,
      params: data.params,
      headers: data.headers,
    }
  }

  buildUrl(data: Pick<AppApiSendConfig, 'action' | 'id' | 'resource' | 'absoluteUrl'>) {
    if (data.absoluteUrl) return data.absoluteUrl
    let _url = data.resource || this.resource
    if (data.id) _url += `/${data.id}`
    if (data.action) _url += `/${data.action}`
    if (data.action?.endsWith('/')) _url = _url.slice(0, -1)
    return _url
  }
}

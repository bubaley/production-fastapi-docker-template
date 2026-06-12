export type ErrorData = {
    code: string
    message: string
    details?: unknown[]
}

export type ResultData<T = unknown> = {
    data: T
    error: ErrorData | null
    success: boolean
}

import moment from 'moment'


const formats = {
  date: 'DD.MM.YYYY',
  time: 'HH:mm',
  dateTime: 'DD.MM.YYYY HH:mm',
  dateTimeFull: 'DD.MM.YYYY HH:mm:ss',
}

export type FormatDateConfig = {
  variant?: keyof typeof formats
  utc?: boolean
}

const defaultFormatDateConfig: FormatDateConfig = { variant: undefined, utc: true }

export const formatDate = (date?: string | null, config?: FormatDateConfig) => {
  config = { ...defaultFormatDateConfig, ...config }
  if (!date) return ''
  let variant = config.variant
  if (!variant) {
    variant = date.includes(' ') || date.includes('T') ? 'dateTime' : 'date'
  }
  return moment.utc(date).format(formats[variant])
}

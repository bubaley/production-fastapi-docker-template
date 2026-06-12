
export type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends () => any
      ? T[K]
      : DeepPartial<T[K]>
    : T[K] | undefined;
};

export interface AppModel {
  id?: string | number | null;
}

export const createCodec = <T extends AppModel | AppPagination>({ decode, encode }: AppCodec<T>) => {
  return {
    decode,
    encode,
  }
}

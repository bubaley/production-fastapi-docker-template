from tortoise import BaseDBAsyncClient, connections
from tortoise.models import Model


class BulkManyToManyManager:
    @classmethod
    async def bulk_add(
        cls,
        relations: list[tuple[Model, list[Model]]],
        through_table: str | None = None,
        from_field: str | None = None,
        to_field: str | None = None,
    ):
        values = cls._process_relations(relations)
        if not values:
            return
        attrs = cls._resolve_attrs(values[0], through_table, from_field, to_field)
        return await cls._add(values, **attrs)

    @classmethod
    async def bulk_remove(
        cls,
        relations: list[tuple[Model, list[Model]]],
        through_table: str | None = None,
        from_field: str | None = None,
        to_field: str | None = None,
    ):
        values = cls._process_relations(relations)
        if not values:
            return
        attrs = cls._resolve_attrs(values[0], through_table, from_field, to_field)
        return await cls._remove(values, **attrs)

    @classmethod
    async def bulk_set(
        cls,
        relations: list[tuple[Model, list[Model]]],
        through_table: str | None = None,
        from_field: str | None = None,
        to_field: str | None = None,
    ):
        if not relations:
            return

        from_objs = [from_obj for from_obj, _ in relations]
        values = cls._process_relations(relations)
        attrs = cls._resolve_attrs_from_model(
            from_objs[0],
            values[0][1] if values else None,
            through_table,
            from_field,
            to_field,
        )
        await cls._clear_from_objs(from_objs, **attrs)
        if values:
            await cls._add(values, **attrs)

    @classmethod
    async def _add(cls, relations: list[tuple[Model, Model]], **kwargs):
        db: BaseDBAsyncClient = connections.get('default')

        client_name = db.__class__.__name__.lower()
        is_postgres = 'postgres' in client_name or 'asyncpg' in client_name

        placeholders = []
        values = []

        if is_postgres:
            param_index = 1
            for from_obj, to_obj in relations:
                placeholders.append(f'(${param_index}, ${param_index + 1})')
                values.extend([from_obj.pk, to_obj.pk])
                param_index += 2

            query = f"""
                INSERT INTO {kwargs['through_table']} ({kwargs['from_field']}, {kwargs['to_field']})
                VALUES {', '.join(placeholders)}
                ON CONFLICT ({kwargs['from_field']}, {kwargs['to_field']}) DO NOTHING
            """  # nosec B608
        else:
            for from_obj, to_obj in relations:
                placeholders.append('(?, ?)')
                values.extend([str(from_obj.pk), str(to_obj.pk)])

            query = f"""
                INSERT OR IGNORE INTO {kwargs['through_table']} ({kwargs['from_field']}, {kwargs['to_field']})
                VALUES {', '.join(placeholders)}
            """  # nosec B608

        await db.execute_query(query, values)

    @classmethod
    async def _remove(cls, relations: list[tuple[Model, Model]], **kwargs):
        db: BaseDBAsyncClient = connections.get('default')

        client_name = db.__class__.__name__.lower()
        is_postgres = 'postgres' in client_name or 'asyncpg' in client_name

        conditions = []
        values = []

        if is_postgres:
            param_index = 1
            for from_obj, to_obj in relations:
                conditions.append(
                    f'({kwargs["from_field"]} = ${param_index} AND {kwargs["to_field"]} = ${param_index + 1})'
                )
                values.extend([from_obj.pk, to_obj.pk])
                param_index += 2
        else:
            for from_obj, to_obj in relations:
                conditions.append(f'({kwargs["from_field"]} = ? AND {kwargs["to_field"]} = ?)')
                values.extend([str(from_obj.pk), str(to_obj.pk)])

        query = f'DELETE FROM {kwargs["through_table"]} WHERE {" OR ".join(conditions)}'  # nosec B608
        await db.execute_query(query, values)

    @classmethod
    async def _clear_from_objs(cls, from_objs: list[Model], **kwargs):
        db: BaseDBAsyncClient = connections.get('default')

        client_name = db.__class__.__name__.lower()
        is_postgres = 'postgres' in client_name or 'asyncpg' in client_name

        from_ids = [obj.pk for obj in from_objs]

        if is_postgres:
            placeholders = ', '.join(f'${i + 1}' for i in range(len(from_ids)))
        else:
            placeholders = ', '.join('?' for _ in from_ids)
            from_ids = [str(pk) for pk in from_ids]

        query = f'DELETE FROM {kwargs["through_table"]} WHERE {kwargs["from_field"]} IN ({placeholders})'  # nosec B608
        await db.execute_query(query, from_ids)

    @classmethod
    def _process_relations(cls, relations: list[tuple[Model, list[Model]]]):
        _values, _tables = [], []
        for from_obj, to_objs in relations:
            for to_obj in to_objs:
                _values.append((from_obj, to_obj))
                _tables.append((from_obj._meta.db_table, to_obj._meta.db_table))
        if len(set(_tables)) > 1:
            raise ValueError('Relations must be unique')
        return _values

    @classmethod
    def _resolve_attrs(
        cls,
        relation: tuple[Model, Model],
        through_table: str | None = None,
        from_field: str | None = None,
        to_field: str | None = None,
    ):
        return cls._resolve_attrs_from_model(relation[0], relation[1], through_table, from_field, to_field)

    @classmethod
    def _resolve_attrs_from_model(
        cls,
        from_obj: Model,
        to_obj: Model | None,
        through_table: str | None = None,
        from_field: str | None = None,
        to_field: str | None = None,
    ):
        if not through_table and not from_field and not to_field and to_obj is None:
            raise ValueError('through_table, from_field and to_field must be provided when to_obj is not available')
        from_table = from_obj._meta.db_table
        to_table = to_obj._meta.db_table if to_obj is not None else None
        return {
            'through_table': through_table or f'{from_table}{to_table}',
            'from_field': from_field or f'{from_table}_id',
            'to_field': to_field or f'{to_table}_id',
        }

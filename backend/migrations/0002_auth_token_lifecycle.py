from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0001_initial')]

    initial = False

    operations = [
        ops.CreateModel(
            name='RefreshSession',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='refresh_sessions', on_delete=OnDelete.CASCADE)),
                ('jti', fields.CharField(unique=True, max_length=64)),
                ('family_id', fields.UUIDField(db_index=True)),
                ('expires_at', fields.DatetimeField(auto_now=False, auto_now_add=False)),
                ('revoked_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
                ('replaced_by', fields.CharField(null=True, max_length=64)),
            ],
            options={'table': 'refresh_session', 'app': 'models', 'pk_attr': 'id', 'table_description': 'One issued refresh token. A login starts a family (`family_id`); every refresh revokes the presented'},
            bases=['BaseModel'],
        ),
        # Existing users: add nullable, backfill, then enforce NOT NULL.
        ops.AddField(
            model_name='User',
            name='is_active',
            field=fields.BooleanField(default=True, null=True),
        ),
        ops.AddField(
            model_name='User',
            name='token_version',
            field=fields.IntField(default=0, null=True),
        ),
        ops.RunSQL(
            'UPDATE "user" SET is_active = TRUE WHERE is_active IS NULL; '
            'UPDATE "user" SET token_version = 0 WHERE token_version IS NULL;',
            reverse_sql='SELECT 1;',
        ),
        ops.AlterField(
            model_name='User',
            name='is_active',
            field=fields.BooleanField(default=True),
        ),
        ops.AlterField(
            model_name='User',
            name='token_version',
            field=fields.IntField(default=0),
        ),
        ops.AddField(
            model_name='UserToken',
            name='expires_at',
            field=fields.DatetimeField(null=True, auto_now=False, auto_now_add=False),
        ),
    ]

from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

client = FaunaClient(secret="fnAEPs19i8AAwgvAUehpzR3dnPxVJAlQ9ped02tu")

indexes = client.query(q.paginate(q.indexes()))

print(indexes)
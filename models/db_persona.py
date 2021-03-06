class CAPITALIZE:
    """"Never returns an error, only converts string input value to a capitalized string.

    Example:
        Usage:
         Field('naam', 'string', requires=IS_CAPITALIZED()),
    """

    def __call__(self, value):
        return self.validate(value)

    def validate(self, value):
        if isinstance(value, str):
            return value.capitalize(), None
        else:
            return value, 'Value has to be a string'


db.define_table('person',
                Field('first_name', 'string', required=True, requires=IS_NOT_EMPTY(), label=T('First name')),
                Field('last_name', 'string', required=True, requires=IS_NOT_EMPTY(), label=T('Last name')),
                # using both unique=True and IS_NOT_IN_DB, because IS_NOT_IN_DB enforces that the inserted value is
                # unique on a form level. unique=True enforces this on a database level. This means that if we
                # were to insert a value in any other way than by a form, the inserted value still has to be unique.
                Field('email', 'string', unique=True, requires=[IS_EMAIL(),
                                                                IS_NOT_EMPTY(),
                                                                IS_NOT_IN_DB(db, 'person.email')]
                      ),
                singular=T('Person'),
                plural=T('People'),
                format=lambda r: f'{r.id} <{r.first_name} {r.last_name}>'
                )

db.define_table('role',
                Field('name', 'string', required=True, unique=True, label=T('Name'),
                      requires=[IS_NOT_EMPTY(),
                                CAPITALIZE(),
                                IS_ALPHANUMERIC(),
                                IS_NOT_IN_DB(db, 'role.name')]
                      ),
                singular=T("Role"),
                plural=T('Roles'),
                format=lambda r: r.name
                )

db.define_table('role_membership',
                # rol_id has to be a list of references for it to allow multiple roles within the same
                # role_membership record
                Field('role_ids', 'list:reference role', label=T('Role(s)')),
                Field('begin_date', 'date', requires=IS_EMPTY_OR(IS_DATE()), label=T('Begin date')),
                Field('end_date', 'date', requires=IS_EMPTY_OR(IS_DATE()), label=T('End date')),
                Field('person_id', 'reference person', required=True, label=T('Person')),
                singular=T("Role membership"),
                plural=T('Role memberships'),
                )

# TODO: add features here

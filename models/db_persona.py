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


def installers():
    import json

    @feature_installer("2021-02-23 Auth Groups",
                       who="Kevin Koster",
                       contact="koster.k2001@gmail.com",
                       sqlite_to_backup=db)
    def installer_20210223_auth_groups(handle) -> bool:
        """Installer that inserts records into the db.auth_group table,
        we're installing these because they're used for Role Based Access Control (RBAC).

        :return: boolean indicating whether the function has been completed successfully.
        """

        groups = json.load(handle)

        for group in groups:

            try:
                db.auth_group.insert(role=group, description=group)
            except RuntimeError as e:
                db.rollback()
                raise e

        return True

    @feature_installer("2021-02-23 Roles",
                       who="Kevin Koster",
                       contact="koster.k2001@gmail.com",
                       sqlite_to_backup=db)
    def installer_20210223_roles(handle) -> bool:
        """Installer that inserts records into the db.role table

        :return: boolean indicating whether the function has been completed successfully.
        """
        roles = json.load(handle)

        for role in roles:

            try:
                db.role.insert(name=role)
            except RuntimeError as e:
                db.rollback()
                raise e

        return True

    @feature_installer("2021-02-23 Demo people and their roles",
                       who="Kevin Koster",
                       contact="koster.k2001@gmail.com",
                       sqlite_to_backup=db)
    def installer_20210223_demo_people_and_assigned_roles(handle) -> bool:

        import random
        today = datetime.date.today()

        people = json.load(handle)

        for person in people:

            try:
                person_id = db.person.insert(first_name=person['first_name'],
                                             last_name=person['last_name'],
                                             email=person['email'])

                db.role_membership.insert(role_ids=[random.randint(1, 8)],
                                          begin_date=today - datetime.timedelta(days=10),
                                          end_date=today + datetime.timedelta(days=30),
                                          person_id=person_id)

            except RuntimeError as e:
                db.rollback()
                raise e

        return True


installers()

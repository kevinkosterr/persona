import datetime
from gluon.cache import lazy_cache
from gluon import DAL, Field, current
import glob, os

feature_db = DAL("sqlite://features.sqlite")
feature_db.define_table(
    "feature",
    Field("name", type="string", required=True),
    Field("success", type="boolean", default=False),
    Field("installation_ts", type="datetime", default=datetime.datetime.now()),
    Field("who", "string", comment="feature author(s)"),
    Field("contact", "string", comment="E-mail address"),
    Field("since", "date", comment="When implemented?"),
    Field("reference", comment="Externel see-more reference hyperlink"),
)


def feature_installer(feature_name, who=None, contact=None, since=None, reference=None):
    @lazy_cache(
        "feature_installer-" + feature_name,
        time_expire=365 * 24 * 3600,
        cache_model="ram",
    )
    def decorator(installer):
        feature_row = feature_db(feature_db.feature.name == feature_name).select().first()

        if feature_row is None or feature_row.success is False:
            try:
                # try the installer (the decorated function) and save
                # it's success
                print("Installing", feature_name)
                # test for a folder, which would mean there are json files to handle
                folder = os.path.join(current.request.folder, 'private', 'setup_data', feature_name)
                file_list = glob.glob(os.path.join(folder, '*')) if os.path.exists(folder) else []
                first_file = file_list[0] if file_list else None
                backup_database()
                if first_file:
                    with open(first_file, 'rb') as open_handle:
                        success = bool(installer(handle=open_handle))
                else:
                    success = bool(installer(handle=None))

            finally:
                feature_db.feature.update_or_insert(
                    (
                            feature_db.feature.name == feature_name
                    ),  # this is a query, used for lookup of the record
                    name=feature_name,  # inserted or updated
                    success=success,  # inserted or updated
                    who=who,
                    contact=contact,
                    since=since,
                    reference=reference,
                )

        else:
            # if already succesfully installed: ignore this installer
            print("Feature '{}' already installed.  ".format(feature_name))

        return True

    return decorator

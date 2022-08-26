# Project Structure



# First time


### FastAPI Crud Endpoints
You have to specify keyword arguments after `db` because of the function signature with `*`
Order matters with endpoints, dynamic routes `route/endpoint/{id}` are last


# Testing
In order to run pytest, you have to set `ENVIRONMENT=development` so that the config
can pick it up and set the correct variables.
Note: Config is not actually setting anything in tests, but the config is called in some of the files that are imported and it will error if not set.


## For A Release
================
- [ ] All tests passing
- [ ] Test on local dev
- [ ] (optional) Test on `test` environment
  - [ ] subject to implementation
- [ ] git merge `feature/{feature}` into `master`
  - [ ] git checkout master
  - [ ] git merge feature/{feature}
- [ ] Bump the version in the main `__init__.py` file in `euphoria` directory
  - [ ] git commit -m 'release: v0.3.0 - Migrate Databases'
- [ ] Create a git tag after the bump so that the tag references the bump commit
  - [ ] git tag -m 'v0.3.0'
- [ ] Push branch and tags
  - [ ] git push --tags
- [ ] Pray to Dionysus
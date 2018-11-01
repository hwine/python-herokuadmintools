UPDATE_BEFORE_COMMIT_FILES :=

help:
	@echo "Targets:"
	@echo "    help     show this text"
	@echo "    test     test everything!"
	@echo "    csv      Generate CSV output for today"
	@echo "    email    Generate email output for today"
	@echo "    membership Generate membership output for today"

membership:
	heroku-admin --membership > $$(date -u +%Y-%m-%d_heroku_membership.csv)

email:
	./heroku-2fa.py --email > $$(date -u +%Y-%m-%dT%H:%M:%S%Z_heroku_missing_2FA.csv) \
		|| echo "Some users missing 2fa"

csv:
	./heroku-2fa.py --csv > $$(date -u +%Y-%m-%dT%H:%M:%S%Z_heroku_missing_2FA.csv) \
		|| echo "Some users missing 2fa"

test:
	@echo "No tests yet"
	false

.PHONY:  test

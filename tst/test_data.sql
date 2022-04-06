INSERT INTO user (username, email, password)
VALUES
  ('test', 'test@imdb.com', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'other@imdb.com', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO movie (movie_title, plot, added_by)
VALUES
  ('A Test Movie', 'A super cool test movie', 1)
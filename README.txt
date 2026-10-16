pjug on GitHub Pages (automatic game list)

Repo layout:
  index.html
  make_games.py
  .github/workflows/update-games.yml
  games/
    games.json          (made automatically)
    some-game/index.html
    another-game.html

Steps:
1. Put all of these files in the root of your repo and drop your games into games/.
2. Repo Settings > Pages: pick the main branch and the root folder.
3. Repo Settings > Actions > General > Workflow permissions: choose "Read and write".
4. Every time you push games, the GitHub Action rebuilds games/games.json for you.
   Or run it yourself: python make_games.py, then commit games/games.json.

To rename a game or add a description, edit games/games.json. Your edits are kept.

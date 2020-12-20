local songs = fs.list("album/music")

for x=1, #songs, 1 do
    term.clear()
    print("Now playing " .. songs[x])
    os.sleep(1)
    print("Hold Ctrl+T to skip track")
    shell.execute("music/" .. songs[x])
end

main = do putStrLn "Haskell main()"
          line <- getLine
          putStrLn ("First line from stdin:" ++ line)
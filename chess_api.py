import requests

def post_chess_api(fen, searchmoves=None):
  """Calls the chess API with the given FEN string.

  Args:
    fen: The FEN string representing the chess position.
    searchmoves: Optional list of moves to restrict the search to.

  Returns:
    The JSON response from the API.
  """
  data = {"fen": fen}
  if searchmoves:
    data["searchmoves"] = searchmoves
    
  response = requests.post(
      "https://chess-api.com/v1",
      headers={"Content-Type": "application/json"},
      json=data
  )
  return response.json()

def get_best_move(fen):
  """Gets the best move, continuation, and evaluation for a given FEN 
  from the chess API.

  Args:
    fen: The FEN string representing the chess position.

  Returns:
    A tuple containing:
      - The best move in SAN notation (string).
      - The continuation array (list of strings).
      - The evaluation in centipawns (integer).
  """
  try:
    response = post_chess_api(fen)
    data = response
    move = data["san"]
    continuation = data["continuationArr"]
    evaluation = int(data["centipawns"])
    return move, continuation, evaluation

  except (requests.exceptions.RequestException, KeyError, ValueError) as e:
    print(f"Error getting best move: {e}")
    return "No move found in the API response.", [], None

def get_evaluation(fen):
  response = post_chess_api(fen)
  return int(response["centipawns"])

def evaluate_move(fen, move_san):
  """Evaluates a specific move in SAN notation for the given FEN position.

  Args:
    fen: The FEN string representing the chess position.
    move_san: The move to evaluate in SAN notation (e.g., "e4", "Nf3").

  Returns:
    A dictionary containing the evaluation and continuation for the move, 
    or an error message if the evaluation fails.
  """
  try:
    response = post_chess_api(fen, searchmoves=move_san)
    data = response
    return {
        "evaluation": int(data["centipawns"]),
        "continuation": data["continuationArr"]
    }

  except (requests.exceptions.RequestException, KeyError, ValueError) as e:
    print(f"Error evaluating move: {e}")
    return {"error": f"Error evaluating move: {e}"}

if __name__ == "__main__":
#   fen_string = "8/1P1R4/n1r2B2/3Pp3/1k4P1/6K1/Bppr1P2/2q5 w - - 0 1"
  fen_string = "8/3k2P1/5K2/7Q/8/8/8/8 b - - 0 1"
  print(get_best_move(fen_string)[0])
  print(evaluate_move(fen_string, "f2f3"))
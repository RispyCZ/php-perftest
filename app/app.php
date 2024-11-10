<?php

function connect_to_db() : PDO {
  return new PDO('sqlite:../database.sqlite');
}

function create_table(PDO $pdo) {
  $query = "CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fistname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    address TEXT NOT NULL
  )";
  $pdo->exec($query);
}

function json_response(array $data, int $status) {
  header("Content-Type: application/json");
  header("HTTP/1.1 " . $status . " " . ($status === 200 ? "OK" : "Error"));
  echo json_encode($data);
  die();
}

$db = connect_to_db();

create_table($db);

if(isset($_POST['firstname']) && isset($_POST['lastname']) && isset($_POST['address'])) { 
  $fistname = $_POST['firstname'];
  $lastname = $_POST['lastname'];
  $address = $_POST['address'];

  if(empty($fistname) || empty($lastname) || empty($address)) {
    json_response(['error' => 'All fields are required']);
  }

  $query = "INSERT INTO users (fistname, lastname, address) VALUES (:fistname, :lastname, :address)";
  $statement = $db->prepare($query);
  $statement->bindValue(':fistname', $fistname);
  $statement->bindValue(':lastname', $lastname);
  $statement->bindValue(':address', $address);
  $statement->execute();
  $statement->closeCursor();
  

  json_response(['success' => true, 'id' => $db->lastInsertId()], 200);
}

if(isset($_GET['id'])) {
  $id = $_GET['id'];

  $query = "SELECT * FROM users WHERE id = :id";
  $statement = $db->prepare($query);
  $statement->bindValue(':id', $id);
  $statement->execute();
  $user = $statement->fetch(PDO::FETCH_ASSOC);
  $statement->closeCursor();

  if($user) {
      json_response($user, 200);
  } else {
      json_response(['error' => 'User not found'], 404);
  }
}

json_response(['error' => 'Invalid request'], 400);
?>
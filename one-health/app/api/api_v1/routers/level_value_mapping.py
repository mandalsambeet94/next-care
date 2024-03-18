from fastapi import APIRouter, HTTPException
from app.models.level_value_mapping import LevelValueMapping
from app.database.engine import mycursor, mydb
from typing import List

router = APIRouter(prefix="/level_value_mapping", tags=["questions"])

@router.post("/add_key_criteria/")
def add_key_criteria(mapping: LevelValueMapping):
    level_id = mapping.level_id
    level_type = mapping.level_type
    
    # Insert each allowed value as a separate record
    for allowed_value in mapping.allowed_values:
        sql = "INSERT INTO level_value_mapping (level_id, level_type, allowed_value) VALUES (%s, %s, %s)"
        val = (level_id, level_type, allowed_value)
        mycursor.execute(sql, val)
        mydb.commit()
    
    return {"message": "Key criteria added successfully"}

@router.get("/view_key_criteria/")
def view_key_criteria():
    # Fetch all key criteria
    mycursor.execute("SELECT * FROM level_value_mapping")
    result = mycursor.fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="No key criteria found")
    return {"key_criteria": result}

@router.put("/update_key_criteria/{level_id}")
def update_key_criteria(level_id: str, mapping: LevelValueMapping):
    # Delete existing key criteria for the given level_id
    delete_sql = "DELETE FROM level_value_mapping WHERE level_id = %s"
    delete_val = (level_id,)
    mycursor.execute(delete_sql, delete_val)
    mydb.commit()
    
    # Insert new key criteria
    insert_sql = "INSERT INTO level_value_mapping (level_id, level_type, allowed_value) VALUES (%s, %s, %s)"
    for allowed_value in mapping.allowed_values:
        insert_val = (level_id, mapping.level_type, allowed_value)
        mycursor.execute(insert_sql, insert_val)
        mydb.commit()

    return {"message": f"Key criteria with ID {level_id} updated successfully"}

@router.delete("/delete_key_criteria/{level_id}")
def delete_key_criteria(level_id: str):
    sql = "DELETE FROM level_value_mapping WHERE level_id = %s"
    val = (level_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    if mycursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Key criteria not found")
    return {"message": f"Key criteria with ID {level_id} deleted successfully"}
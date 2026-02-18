import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Manual coordinate mapping for key CoMo Transit stops
# Coordinates extracted from known locations in Columbia, MO
STOP_COORDINATES = {
    "Wabash Station": (38.95344543457031, -92.32564544677734),
    "Tiger Ave & Conley Ave": (38.94431686401367, -92.3298110961914),
    "Tiger Ave at Residence Halls": (38.93836212158203, -92.33079528808594),
    "Green Meadow Rd & Carter Ln": (38.917171478271484, -92.33279418945312),
    "South Providence Medical Plaza": (38.90037155151367, -92.33193969726562),
    "Tiger Ave & Hospital Dr": (38.9383544921875, -92.33065032958984),
    
    # Red Route
    "Columbia Library": (38.951568603515625, -92.34083557128906),
    "Broadway & West Blvd": (38.95202636718750, -92.35234069824219),
    "Crossroads shopping center": (38.95412063598633, -92.37246704101562),
    "Walmart West": (38.95450210571289, -92.37955474853516),
    
    # Gold Route  
    "Rogers St & 5th St": (38.95684814453125, -92.33177185058594),
    "Oak Towers": (38.96001052856445, -92.33866119384766),
    "Food Pantry": (38.959560394287110, -92.35467529296875),
    "Health Dept": (38.96091079711914, -92.36813354492188),
    "Columbia Mall": (38.96571731567383, -92.3736343383789),
    
    # Orange Route
    "Wilkes Blvd & Seventh St": (38.96037292480469, -92.32868194580078),
    "Ashley Street Center": (38.967464447021484, -92.31612396240234),
    "Rangeline & Elleta Blvd": (38.974822998046875, -92.32635498046875),
    "Smiley Ln & Derby Ridge": (38.99324417114258, -92.31729888916016),
    "Brown School Rd & Rangeline": (39.00096130371094, -92.32176208496094),
    "Rangeline & Blue Ridge": (38.98384094238281, -92.3261947631836),
    "Rangeline & Boone Electric": (38.966217041015625, -92.32479095458984),
    
    # Blue Route
    "Whitegate & Sylvan": (38.96800994873047, -92.30139923095703),
    "Clark Ln & Burger King": (38.96379089355469, -92.2874984741211),
    "Clark Ln & St Charles Rd": (38.96342468261719, -92.29664611816406),
    "Ballenger Ln & M Gravel": (38.98517608642578, -92.26456451416016),
    "Hanover Estate": (38.967430114746094, -92.2820053100586),
    "Clark Ln & Taco Bell": (38.96392059326172, -92.28890228271484),
    
    # Green Route
    "Hitt St & University Ave": (38.946529388427734, -92.3256607055664),
    "Boone Hospital": (38.949188232421875, -92.31717681884766),
    "Broadway & Broadway Village": (38.947357177734375, -92.30355834960938),
    "Women's & Childrens H": (38.95755386352539, -92.28948211669922),
    "Conley Rd & Trimble": (38.94799041748047, -92.29901123046875),
    "Plaza 3 & 4": (38.95022964477539, -92.31441497802734),
    "Paquin Tower": (38.94768142700195, -92.32365417480469),
}

def update_transit_coordinates():
    """Update transit stops with known coordinates."""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("📍 Updating transit stop coordinates...")
    
    updated_count = 0
    for stop_name, (lat, lng) in STOP_COORDINATES.items():
        cur.execute("""
            UPDATE transit_stops
            SET location_geo = ST_GeogFromText('POINT(%s %s)')
            WHERE stop_name = %s
        """, (lng, lat, stop_name))
        
        if cur.rowcount > 0:
            updated_count += cur.rowcount
            print(f"  ✓ Updated: {stop_name}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n✅ Updated {updated_count} transit stops with coordinates!")

if __name__ == "__main__":
    update_transit_coordinates()

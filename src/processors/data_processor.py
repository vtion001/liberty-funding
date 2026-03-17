"""Data Processor - Combine and format data from multiple sources"""
from typing import List, Dict
from datetime import datetime


class DataProcessor:
    """Process and combine data from multiple sources"""
    
    def __init__(self):
        self.processed_data = []
    
    def process(self, gohighlevel_data: List[Dict], zoho_data: List[Dict]) -> List[Dict]:
        """
        Process and combine data from GoHighLevel and Zoho
        
        Args:
            gohighlevel_data: Data from GoHighLevel
            zoho_data: Data from Zoho
            
        Returns:
            Combined and processed data
        """
        combined = []
        
        # Add GoHighLevel data
        for record in gohighlevel_data:
            combined.append(self._normalize_record(record, "GoHighLevel"))
        
        # Add Zoho data
        for record in zoho_data:
            combined.append(self._normalize_record(record, "Zoho"))
        
        # Sort by timestamp (newest first)
        combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        self.processed_data = combined
        return combined
    
    def _normalize_record(self, record: Dict, source: str) -> Dict:
        """Normalize record to standard format"""
        return {
            "date": self._format_date(record.get("timestamp")),
            "source": source,
            "campaign": record.get("campaign_name", record.get("campaign_id", "")),
            "bounce_rate": float(record.get("bounce_rate", 0)),
            "sent_count": int(record.get("sent_count", 0)),
            "bounce_count": int(record.get("bounce_count", 0)),
            "timestamp": record.get("timestamp", datetime.now().isoformat())
        }
    
    def _format_date(self, timestamp: str) -> str:
        """Format timestamp to readable date"""
        if not timestamp:
            return datetime.now().strftime("%Y-%m-%d")
        
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except:
            return str(timestamp)[:10]
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.processed_data:
            return {"total": 0, "avg_bounce_rate": 0}
        
        total = len(self.processed_data)
        avg_bounce = sum(r["bounce_rate"] for r in self.processed_data) / total
        
        return {
            "total_records": total,
            "avg_bounce_rate": round(avg_bounce, 2),
            "gohighlevel_count": len([r for r in self.processed_data if r["source"] == "GoHighLevel"]),
            "zoho_count": len([r for r in self.processed_data if r["source"] == "Zoho"])
        }


if __name__ == "__main__":
    processor = DataProcessor()
    # Test with sample data
    sample_ghl = [{"campaign_name": "Test 1", "bounce_rate": 5, "sent_count": 100, "bounce_count": 5}]
    sample_zoho = [{"campaign_name": "Test 2", "bounce_rate": 3, "sent_count": 200, "bounce_count": 6}]
    
    result = processor.process(sample_ghl, sample_zoho)
    print(f"Processed {len(result)} records")
    print(processor.get_summary())

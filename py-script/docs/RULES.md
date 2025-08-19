1. **API URL NEEDS TO REMAIN**  
   `https://api.cycle.tools/api/Stream/SubmitStreamData?api_key=REDACTED`

2. **POSTED MESSAGE NEEDS TO REMAIN**  
   ```json
   {
     "streamid": "YOUR-STREAM-ID",
     "messagetype": "UPSERT",
     "dates": [ "{{time}}" ],
     "values": [ {{close}} ]
   }
   ```

3. **YOUR-STREAM-ID** can be any collection of letters. It is merely for reference to the relevant symbol in the Cycles app.

4. **Limits (Public/Demo Plan for CoinGecko)**  
   - Up to ~30 requests per minute, but real-world usage may be more restrictive depending on endpoint and traffic.  
   - Monthly cap: ~10,000 requests maximum.
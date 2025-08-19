# Cycles API Developer Documentation

## Quick Start

The Cycles API allows you to stream real-time data to your Cycles app dashboard. Send time-series data via simple HTTP POST requests.

## Basic Usage

### HTTP Request
```http
POST https://api.cycle.tools/api/Stream/SubmitStreamData?api_key=YOUR-API-KEY

Content-Type: application/json

{
  "streamid": "YOUR-STREAM-ID",
  "messagetype": "UPSERT",
  "dates": ["2024-01-15T10:30:00Z"],
  "values": [42.50]
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `streamid` | string | Yes | Unique identifier for your data stream, merely for reference |
| `messagetype` | string | Yes | Always use `"UPSERT"` |
| `dates` | array | Yes | ISO timestamp in array format |
| `values` | array | Yes | Numeric value in array format |


## Best Practices

### Timeframe Limits
- **Minimum timeframe**: 1 minute intervals

### Stream Limits
- **Analyst Pro**: 10 streams by default
- Use descriptive stream IDs for organization

### Best Practices
1. **Handle errors gracefully** with retry logic
2. **Use consistent timestamps** in ISO format
3. **Monitor your stream count** to stay within limits
4. **Use meaningful stream IDs** for dashboard organization
5. **Respect data exchange rate limits** to ensure reliable data delivery


## Getting Your API Key

1. Log into your Cycles account
2. Navigate to [/account/api](https://app.cycles.org/account/api)
3. Generate or copy your API key

## Examples

- [python](https://github.com/composedbymax/crypto-cycles-feed/tree/main/py-script)

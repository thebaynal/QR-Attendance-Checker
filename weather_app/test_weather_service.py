# test_weather_service.py
"""Simple tests for weather service."""

import asyncio
from mod6_labs.weather_service import WeatherService, WeatherServiceError


async def test_valid_city():
    """Test fetching weather for a valid city."""
    service = WeatherService()
    try:
        data = await service.get_weather("London")
        print(f"✅ Successfully fetched weather for {data['name']}")
        print(f"   Temperature: {data['main']['temp']}°C")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_invalid_city():
    """Test handling of invalid city."""
    service = WeatherService()
    try:
        await service.get_weather("InvalidCityXYZ123")
        print("❌ Should have raised an error")
        return False
    except WeatherServiceError as e:
        print(f"✅ Correctly handled error: {e}")
        return True


async def test_empty_city():
    """Test handling of empty city name."""
    service = WeatherService()
    try:
        await service.get_weather("")
        print("❌ Should have raised an error")
        return False
    except WeatherServiceError as e:
        print(f"✅ Correctly handled error: {e}")
        return True


async def run_tests():
    """Run all tests."""
    print("Running Weather Service Tests\n")
    print("=" * 50)
    
    results = []
    results.append(await test_valid_city())
    results.append(await test_invalid_city())
    results.append(await test_empty_city())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")


if __name__ == "__main__":
    asyncio.run(run_tests())
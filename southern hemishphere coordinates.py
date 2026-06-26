from astropy.coordinates import SkyCoord
import astropy.units as u

print("Calculating heliographic coordinates for tracked centroids...")

heliographic_coordinates = []

# Iterate through the tracked centroids and their corresponding FITS files
for i, centroid_tuple in enumerate(tracked_centroids_subset):
    if centroid_tuple is not None:
        # Load the map corresponding to the current frame
        smap = sunpy.map.Map(last_three_fits_files[i])

        # Convert pixel coordinates (row, col) to world coordinates (heliographic latitude/longitude)
        # smap.pixel_to_world expects (x, y) where x is horizontal (column) and y is vertical (row)
        # centroid_tuple is (row, col)
        world_coords = smap.pixel_to_world(centroid_tuple[1] * u.pixel, centroid_tuple[0] * u.pixel)

        # Explicitly convert to HeliographicStonyhurst frame to ensure lat/lon access
        heliographic_coord_stonyhurst = world_coords.heliographic_stonyhurst

        heliographic_coordinates.append({
            'date': smap.date,
            'latitude': heliographic_coord_stonyhurst.lat.to(u.deg),
            'longitude': heliographic_coord_stonyhurst.lon.to(u.deg)
        })
        print(f"Frame {i} ({smap.date.strftime('%Y-%m-%d')}) - Lat: {heliographic_coord_stonyhurst.lat.to(u.deg):.2f}, Lon: {heliographic_coord_stonyhurst.lon.to(u.deg):.2f}")
    else:
        heliographic_coordinates.append(None)
        print(f"Frame {i}: No centroid data.")

print("\nHeliographic Coordinates of Tracked Active Region:")
for coord_info in heliographic_coordinates:
    if coord_info:
        print(f"Date: {coord_info['date'].strftime('%Y-%m-%d %H:%M:%S')}, Latitude: {coord_info['latitude']:.2f}, Longitude: {coord_info['longitude']:.2f}")

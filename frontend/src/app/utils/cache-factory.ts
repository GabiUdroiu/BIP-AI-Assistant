import { Observable, of } from 'rxjs';
import { tap, shareReplay } from 'rxjs/operators';
import { ApiResponse } from '../models/api-response';

/**
 * Generic caching wrapper for Observable responses.
 * Caches the first response and returns it for subsequent calls.
 */
export class CacheFactory {
  /**
   * Create a cached observable that stores results in the provided map.
   *
   * @param cache - Map to store cached values
   * @param cacheKey - Unique key for this cache entry
   * @param fetcher - Function that returns the Observable to cache
   * @returns Observable that caches and returns the response
   */
  static cached<T>(
    cache: Map<string, T | null>,
    cacheKey: string,
    fetcher: () => Observable<ApiResponse<T>>
  ): Observable<ApiResponse<T>> {
    // Return cached value if available
    if (cache.has(cacheKey)) {
      return of({ data: cache.get(cacheKey) } as ApiResponse<T>);
    }

    // Fetch, cache, and return
    return fetcher().pipe(
      tap((res) => cache.set(cacheKey, res.data || null)),
      shareReplay(1)
    );
  }

  /**
   * Invalidate a cache entry.
   */
  static invalidate(cache: Map<string, any>, cacheKey?: string): void {
    if (cacheKey) {
      cache.delete(cacheKey);
    } else {
      cache.clear();
    }
  }
}

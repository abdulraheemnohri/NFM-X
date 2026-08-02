package com.nfm.client

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

class NFMClient(
    private val baseUrl: String = "http://localhost:8765",
    private val apiKey: String? = null
) {
    private val client = OkHttpClient()
    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private fun buildRequest(method: String, path: String, body: String? = null): Request {
        val builder = Request.Builder().url("$baseUrl$path")
        apiKey?.let { builder.header("Authorization", "Bearer $it") }
        builder.header("Content-Type", "application/json")
        builder.header("Accept", "application/json")
        when (method) {
            "GET" -> builder.get()
            "POST" -> builder.post(body!!.toRequestBody(jsonMediaType))
            "PUT" -> builder.put(body!!.toRequestBody(jsonMediaType))
            "DELETE" -> builder.delete()
        }
        return builder.build()
    }

    suspend fun createMemory(memory: NFMMemory): Result<NFMMemory> = withContext(Dispatchers.IO) {
        try {
            val request = buildRequest("POST", "/v1/memory/", gson.toJson(memory))
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                Result.success(gson.fromJson(body, NFMMemory::class.java))
            }
        } catch (e: Exception) { Result.failure(e) }
    }

    suspend fun getMemory(memoryId: String): Result<NFMMemory> = withContext(Dispatchers.IO) {
        try {
            val request = buildRequest("GET", "/v1/memory/$memoryId")
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                Result.success(gson.fromJson(body, NFMMemory::class.java))
            }
        } catch (e: Exception) { Result.failure(e) }
    }

    suspend fun searchMemories(query: String, agentId: String? = null, limit: Int = 10): Result<SearchResponse> = withContext(Dispatchers.IO) {
        try {
            val searchQuery = SearchQuery(query = query, agent_id = agentId, limit = limit)
            val request = buildRequest("POST", "/v1/memory/search", gson.toJson(searchQuery))
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                Result.success(gson.fromJson(body, SearchResponse::class.java))
            }
        } catch (e: Exception) { Result.failure(e) }
    }

    suspend fun health(): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val request = buildRequest("GET", "/health")
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) return@withContext Result.failure(IOException("HTTP ${response.code}"))
                val body = response.body?.string() ?: return@withContext Result.failure(IOException("Empty"))
                @Suppress("UNCHECKED_CAST")
                Result.success(gson.fromJson(body, Map::class.java) as Map<String, Any>)
            }
        } catch (e: Exception) { Result.failure(e) }
    }
}

data class NFMMemory(
    val id: String? = null,
    val root_id: String? = null,
    val version: Int = 1,
    val type: String,
    val content: String,
    val subtype: String? = null,
    val agent_id: String? = null,
    val source_id: String? = null,
    val confidence: Double = 0.7,
    val importance: Double = 0.5,
    val status: String = "active",
    val created_at: String? = null,
    val metadata: Map<String, Any>? = null
)

data class SearchQuery(
    val query: String,
    val agent_id: String? = null,
    val limit: Int = 10,
    val memory_types: List<String>? = null
)

data class SearchResponse(
    val query: String,
    val results: List<MemoryResult>,
    val count: Int
)

data class MemoryResult(
    val id: String,
    val type: String,
    val content: String,
    val confidence: Double,
    val importance: Double,
    val score: Double
)

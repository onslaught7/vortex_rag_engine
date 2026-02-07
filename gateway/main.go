package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/redis/go-redis/v9"
)


// Define the Data Contract we expect from the user
type IngestRequest struct {
	UserID string `json:"user_id"`
	DocumentID string `json:"document_id"`
	Content string `json:"content"`
}

var ctx = context.Background()

func main() {
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "localhost:6379" // Default for local testing
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	// Test connection
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Could not connect to Redis: %v", err)
	}
	
	app := fiber.New()

	app.Post("/ingest", func(c *fiber.Ctx) error {
		// Parse JSON
		payload := new(IngestRequest)
		if err := c.BodyParser(payload); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Invalid JSON"})
		}

		// Push to Redis
		err := rdb.LPush(ctx, "ingestion_queue", c.Body()).Err()
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": "Redis Queue Failed"})
		}

		// Response Instantly
		return c.Status(202).JSON(fiber.Map{
			"status": "accepted",
			"message": "Document Queued for Processing",
			"data": payload.DocumentID,
		})
	})

	log.Fatal(app.Listen(":8080"))
}
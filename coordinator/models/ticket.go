package models

import (
	"encoding/json"
	"time"

	"github.com/gobuffalo/nulls"
	"github.com/gobuffalo/pop/v6"
	"github.com/gobuffalo/validate/v3"
	"github.com/gobuffalo/validate/v3/validators"
	"github.com/gofrs/uuid"
)

// Ticket is used by pop to map your tickets database table to your go code.
type Ticket struct {
	ID            uuid.UUID      `json:"id" db:"id"`
	CreatedAt     time.Time      `json:"created_at" db:"created_at"`
	ExpiresAt     time.Time      `json:"expires_at" db:"expires_at"`
	FinishedAt    nulls.Time     `json:"finished_at" db:"finished_at"`
	SpotID        uuid.UUID      `json:"spot_id" db:"spot_id"`
	Spot          *Spot          `json:"spot,omitempty" belongs_to:"spot"`
	UserID        uuid.UUID      `json:"user_id" db:"user_id"`
	User          *User          `json:"user,omitempty" belongs_to:"user"`
	Notifications []Notification `json:"notifications,omitempty" has_many:"notifications"`
}

// String is not required by pop and may be deleted
func (t Ticket) String() string {
	jt, _ := json.Marshal(t)
	return string(jt)
}

// Tickets is not required by pop and may be deleted
type Tickets []Ticket

// String is not required by pop and may be deleted
func (t Tickets) String() string {
	jt, _ := json.Marshal(t)
	return string(jt)
}

// Validate gets run every time you call a "pop.Validate*" (pop.ValidateAndSave, pop.ValidateAndCreate, pop.ValidateAndUpdate) method.
// This method is not required and may be deleted.
func (t *Ticket) Validate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.Validate(
		&validators.UUIDIsPresent{Field: t.SpotID, Name: "SpotID"},
		&validators.UUIDIsPresent{Field: t.UserID, Name: "UserID"},
		&validators.TimeIsPresent{Field: t.CreatedAt, Name: "CreatedAt"},
		&validators.TimeIsPresent{Field: t.ExpiresAt, Name: "ExpiresAt"},
	), nil
}

// ValidateCreate gets run every time you call "pop.ValidateAndCreate" method.
// This method is not required and may be deleted.
func (t *Ticket) ValidateCreate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

// ValidateUpdate gets run every time you call "pop.ValidateAndUpdate" method.
// This method is not required and may be deleted.
func (t *Ticket) ValidateUpdate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

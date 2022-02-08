package models

import (
	"encoding/json"
	"time"

	"github.com/gobuffalo/pop/v6"
	"github.com/gobuffalo/validate/v3"
	"github.com/gobuffalo/validate/v3/validators"
	"github.com/gofrs/uuid"
)

// Notification is used by pop to map your notifications database table to your go code.
type Notification struct {
	ID        uuid.UUID `json:"id" db:"id"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	Type      string    `json:"type" db:"type"`
	TicketID  uuid.UUID `json:"ticket_id" db:"ticket_id"`
	Ticket    *Ticket   `json:"ticket,omitempty" belongs_to:"ticket"`
}

// String is not required by pop and may be deleted
func (n Notification) String() string {
	jn, _ := json.Marshal(n)
	return string(jn)
}

// Notifications is not required by pop and may be deleted
type Notifications []Notification

// String is not required by pop and may be deleted
func (n Notifications) String() string {
	jn, _ := json.Marshal(n)
	return string(jn)
}

// Validate gets run every time you call a "pop.Validate*" (pop.ValidateAndSave, pop.ValidateAndCreate, pop.ValidateAndUpdate) method.
// This method is not required and may be deleted.
func (n *Notification) Validate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.Validate(
		&validators.StringInclusion{Field: n.Type, Name: "Type"},
		&validators.UUIDIsPresent{Field: n.TicketID, Name: "TicketID"},
	), nil
}

// ValidateCreate gets run every time you call "pop.ValidateAndCreate" method.
// This method is not required and may be deleted.
func (n *Notification) ValidateCreate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

// ValidateUpdate gets run every time you call "pop.ValidateAndUpdate" method.
// This method is not required and may be deleted.
func (n *Notification) ValidateUpdate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

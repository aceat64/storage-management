package models

import (
	"encoding/json"

	"github.com/gobuffalo/pop/v6"
	"github.com/gobuffalo/validate/v3"
	"github.com/gobuffalo/validate/v3/validators"
	"github.com/gofrs/uuid"
)

// Spot is used by pop to map your spots database table to your go code.
type Spot struct {
	ID      uuid.UUID `json:"id" db:"id"`
	Name    string    `json:"name" db:"name"`
	AreaID  uuid.UUID `json:"area_id" db:"area_id"`
	Area    *Area     `json:"area,omitempty" belongs_to:"area"`
	Tickets []Ticket  `json:"tickets,omitempty" has_many:"tickets"`
}

// String is not required by pop and may be deleted
func (s Spot) String() string {
	js, _ := json.Marshal(s)
	return string(js)
}

// Spots is not required by pop and may be deleted
type Spots []Spot

// String is not required by pop and may be deleted
func (s Spots) String() string {
	js, _ := json.Marshal(s)
	return string(js)
}

// Validate gets run every time you call a "pop.Validate*" (pop.ValidateAndSave, pop.ValidateAndCreate, pop.ValidateAndUpdate) method.
// This method is not required and may be deleted.
func (s *Spot) Validate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.Validate(
		&validators.StringIsPresent{Field: s.Name, Name: "Name"},
		&validators.UUIDIsPresent{Field: s.AreaID, Name: "AreaID"},
	), nil
}

// ValidateCreate gets run every time you call "pop.ValidateAndCreate" method.
// This method is not required and may be deleted.
func (s *Spot) ValidateCreate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

// ValidateUpdate gets run every time you call "pop.ValidateAndUpdate" method.
// This method is not required and may be deleted.
func (s *Spot) ValidateUpdate(tx *pop.Connection) (*validate.Errors, error) {
	return validate.NewErrors(), nil
}

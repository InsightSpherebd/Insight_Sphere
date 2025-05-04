<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Course extends Model
{
    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'title',
        'description',
        'date',
        'duration',
        'fee',
        'capacity',
        'location',
        'is_online',
        'session_link',
        'is_published',
        'registration_open',
        'payment_methods',
        'allow_bkash',
        'allow_nagad',
        'allow_rocket',
        'allow_cards',
        'creator_id',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'date' => 'datetime',
        'is_online' => 'boolean',
        'is_published' => 'boolean',
        'registration_open' => 'boolean',
        'allow_bkash' => 'boolean',
        'allow_nagad' => 'boolean',
        'allow_rocket' => 'boolean',
        'allow_cards' => 'boolean',
    ];

    /**
     * Get the creator of the course
     */
    public function creator()
    {
        return $this->belongsTo(User::class, 'creator_id');
    }

    /**
     * Get all videos related to the course
     */
    public function videos()
    {
        return $this->hasMany(CourseVideo::class);
    }

    /**
     * Get all materials related to the course
     */
    public function materials()
    {
        return $this->hasMany(CourseMaterial::class);
    }

    /**
     * Get all users registered for the course
     */
    public function participants()
    {
        return $this->belongsToMany(User::class, 'registrations')
            ->withPivot('payment_status')
            ->withTimestamps();
    }

    /**
     * Check if a user is registered for this course
     */
    public function isRegistered(User $user)
    {
        return $this->participants()->where('user_id', $user->id)->exists();
    }

    /**
     * Get available seats in the course
     */
    public function availableSeats()
    {
        if ($this->capacity <= 0) {
            return 'Unlimited';
        }
        $registered = $this->participants()->count();
        return $this->capacity - $registered;
    }

    /**
     * Get the number of people who have completed payment
     */
    public function paidParticipants()
    {
        return $this->participants()
            ->wherePivot('payment_status', 'completed')
            ->count();
    }
}

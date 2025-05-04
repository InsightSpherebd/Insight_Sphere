<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'username',
        'email', 
        'full_name',
        'phone',
        'password',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * Check if user has admin role
     *
     * @return bool
     */
    public function isAdmin()
    {
        return in_array($this->role, ['admin', 'super_admin']);
    }

    /**
     * Check if user has super admin role
     *
     * @return bool
     */
    public function isSuperAdmin()
    {
        return $this->role === 'super_admin';
    }
    
    /**
     * Get all courses that the user is registered for
     */
    public function courses()
    {
        return $this->belongsToMany(Course::class, 'registrations')
            ->withPivot('payment_status')
            ->withTimestamps();
    }

    /**
     * Get all payments made by the user
     */
    public function payments()
    {
        return $this->hasMany(Payment::class);
    }

    /**
     * Get all certificates issued to the user
     */
    public function certificates()
    {
        return $this->hasMany(Certificate::class);
    }
}

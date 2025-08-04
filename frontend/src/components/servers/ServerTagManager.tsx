import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemSecondaryAction,
  ListItemText,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import serverService, { ServerTag } from '../../services/serverService';

const ServerTagManager: React.FC = () => {
  const [tags, setTags] = useState<ServerTag[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog state
  const [dialogOpen, setDialogOpen] = useState<boolean>(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [currentTag, setCurrentTag] = useState<ServerTag | null>(null);
  const [tagName, setTagName] = useState<string>('');
  const [tagDescription, setTagDescription] = useState<string>('');
  const [dialogError, setDialogError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  const fetchTags = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await serverService.getTags();
      setTags(data);
    } catch (err) {
      console.error('Error fetching tags:', err);
      setError('Failed to load server tags. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  const handleOpenCreateDialog = () => {
    setDialogMode('create');
    setCurrentTag(null);
    setTagName('');
    setTagDescription('');
    setDialogError(null);
    setDialogOpen(true);
  };

  const handleOpenEditDialog = (tag: ServerTag) => {
    setDialogMode('edit');
    setCurrentTag(tag);
    setTagName(tag.name);
    setTagDescription(tag.description || '');
    setDialogError(null);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const validateTagForm = (): boolean => {
    if (!tagName.trim()) {
      setDialogError('Tag name is required');
      return false;
    }
    
    // Check for duplicate tag names (except when editing the same tag)
    if (dialogMode === 'create' || (currentTag && tagName !== currentTag.name)) {
      const tagExists = tags.some(tag => tag.name.toLowerCase() === tagName.trim().toLowerCase());
      if (tagExists) {
        setDialogError('A tag with this name already exists');
        return false;
      }
    }
    
    return true;
  };

  const handleSaveTag = async () => {
    if (!validateTagForm()) return;
    
    setSaving(true);
    setDialogError(null);
    
    try {
      if (dialogMode === 'create') {
        await serverService.createTag({
          name: tagName.trim(),
          description: tagDescription.trim() || undefined,
        });
      } else if (dialogMode === 'edit' && currentTag) {
        await serverService.updateTag(currentTag.id, {
          name: tagName.trim(),
          description: tagDescription.trim() || undefined,
        });
      }
      
      await fetchTags();
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving tag:', err);
      setDialogError('Failed to save tag. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    if (!window.confirm('Are you sure you want to delete this tag?')) return;
    
    try {
      await serverService.deleteTag(tagId);
      await fetchTags();
    } catch (err) {
      console.error('Error deleting tag:', err);
      setError('Failed to delete tag. Please try again.');
    }
  };

  if (loading && tags.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h1">
          Server Tags
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          Add New Tag
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button color="inherit" size="small" onClick={fetchTags} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}

      <Card>
        <CardHeader title="Manage Tags" />
        <Divider />
        <CardContent>
          {tags.length === 0 ? (
            <Typography color="textSecondary" align="center" py={3}>
              No tags found. Create your first tag to get started.
            </Typography>
          ) : (
            <List>
              {tags.map((tag) => (
                <ListItem key={tag.id} divider>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center">
                        <Chip label={tag.name} size="small" sx={{ mr: 2 }} />
                        <Typography variant="body1">{tag.name}</Typography>
                      </Box>
                    }
                    secondary={tag.description || 'No description'}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="edit"
                      onClick={() => handleOpenEditDialog(tag)}
                      sx={{ mr: 1 }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDeleteTag(tag.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Tag Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' ? 'Create New Tag' : 'Edit Tag'}
        </DialogTitle>
        <DialogContent>
          {dialogError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {dialogError}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Tag Name"
            fullWidth
            value={tagName}
            onChange={(e) => setTagName(e.target.value)}
            required
            error={!tagName.trim()}
            helperText={!tagName.trim() ? 'Tag name is required' : ''}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description (Optional)"
            fullWidth
            value={tagDescription}
            onChange={(e) => setTagDescription(e.target.value)}
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveTag}
            color="primary"
            disabled={saving}
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {dialogMode === 'create' ? 'Create' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServerTagManager;